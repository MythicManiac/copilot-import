import sys
import webbrowser
from datetime import datetime, timedelta
from time import sleep
from typing import Optional

import requests
from requests import Response

OAUTH_CLIENT_ID = "01ab8ac9400c4e429b23"  # GitHub's VSCode auth client ID
OAUTH_SCOPE = "read:user"
OAUTH_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
REQUEST_HEADERS = {
    "content-type": "application/json",
    "accept": "application/json",
}
REPO_URL = "https://github.com/MythicManiac/copilot-import"


class LoginSession:
    def __init__(
        self,
        device_code: str,
        user_code: str,
        verification_uri: str,
        expires_in: int,
        interval: int,
    ):
        self.device_code = device_code
        self.user_code = user_code
        self.verification_uri = verification_uri
        self.expires_in = expires_in
        self.interval = interval


class AccessToken:
    def __init__(self, access_token: str, token_type: str, scope: str):
        self.access_token = access_token
        self.token_type = token_type
        self.scope = scope


class CopilotToken:
    def __init__(self, token: str, expires_at: int):
        self.token = token
        self.expires_at = expires_at


def unbuffered_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def log_failure_response(response: Response) -> None:
    unbuffered_print(f"Response status code: {response.status_code}")
    unbuffered_print(f"Response content:\n\n{response.content}\n")
    unbuffered_print(f"If you believe this is a bug, open an issue at {REPO_URL}")


def get_login_session() -> LoginSession:
    response = requests.post(
        "https://github.com/login/device/code",
        json={
            "client_id": OAUTH_CLIENT_ID,
            "scope": OAUTH_SCOPE,
        },
        headers=REQUEST_HEADERS,
    )
    try:
        response.raise_for_status()
        return LoginSession(**response.json())
    except Exception:
        unbuffered_print("Unhandled error occurred")
        log_failure_response(response)
        raise


def wait_for_access_token(session: LoginSession) -> Optional[AccessToken]:
    expiry = datetime.now() + timedelta(seconds=session.expires_in)
    has_expired = False
    access_token: Optional[AccessToken] = None

    unbuffered_print(f"Polling for login session status until {expiry.isoformat()}")
    while access_token is None and not has_expired:
        sleep(session.interval)
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": OAUTH_CLIENT_ID,
                "device_code": session.device_code,
                "grant_type": OAUTH_GRANT_TYPE,
            },
            headers=REQUEST_HEADERS,
        )
        try:
            response.raise_for_status()
            response_data = response.json()
            if "error" in response_data:
                unbuffered_print(
                    f"Polling for login session status: {response_data['error']}",
                )
            else:
                access_token = AccessToken(**response.json())
            has_expired = datetime.now() >= expiry
        except Exception:
            unbuffered_print("Unhandled error occurred")
            log_failure_response(response)
            raise
    return access_token


def get_copilot_token(access_token: AccessToken) -> Optional[CopilotToken]:
    response = requests.get(
        "https://api.github.com/copilot_internal/token",
        headers={
            **REQUEST_HEADERS,
            **{
                "Authorization": f"token {access_token.access_token}",
            },
        },
    )
    if response.status_code == 200:
        return CopilotToken(**response.json())
    else:
        unbuffered_print(
            "It looks like you don't have access to Copilot, "
            "or we've hit some other error.",
        )
        unbuffered_print(
            "Normally an account that has no access to Copilot "
            "will see a 404 error.\n",
        )
        log_failure_response(response)
        return None


def do_login() -> None:
    unbuffered_print("Initializing a login session...")
    login_session = get_login_session()
    unbuffered_print(f"YOUR DEVICE AUTHORIZATION CODE IS: {login_session.user_code}")
    unbuffered_print(
        f"Input the code to {login_session.verification_uri} "
        "in order to authenticate.\n",
    )
    try:
        webbrowser.open(login_session.verification_uri)
    except Exception:
        unbuffered_print("Failed to open a browser")
    access_token = wait_for_access_token(login_session)
    if access_token:
        copilot_token = get_copilot_token(access_token)
        if copilot_token:
            expires_at = datetime.utcfromtimestamp(copilot_token.expires_at)
            unbuffered_print("Successfully obtained copilot token!\n\n")
            unbuffered_print(f"YOUR TOKEN: {copilot_token.token}")
            unbuffered_print(f"EXPIRES AT: {expires_at.isoformat()}\n")
            unbuffered_print("You can add the token to your environment e.g. with")
            unbuffered_print(f"export GITHUB_COPILOT_TOKEN={copilot_token.token}")
        else:
            unbuffered_print("Failed to fetch copilot token")
    else:
        unbuffered_print("Failed to log in")


def run() -> None:
    do_login()
