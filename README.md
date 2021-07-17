# Copilot Importer

Why write code when you can import it directly from GitHub Copilot?

## What is Copilot Importer?

The `copilot` python module will dynamically generate any function imported
by leveraging the GitHub Copilot service.

## How do I use Copilot Importer?

You can install copilot-importer via pip (e.g. `pip install copilot-importer`).

Additionally and importantly, you need a GitHub Copilot API token. See
[How do I get an authentication token](#how-do-I-get-an-authentication-token).

Once you have your token, set it to the environment variable
`GITHUB_COPILOT_TOKEN`.

```shell
export GITHUB_COPILOT_TOKEN=xxxxxxxxxxxxxxxxxxxx
```

Finally, before the dynamic importing feature is enabled, you must run the
`copilot.install` method.

```python
# Enable copilot importer
from copilot import install
install()
```

After all of the above has been taken care of, you should be able to import
anything you want directly from GitHub Copilot:

```python
>>> from copilot import install
>>> install()

>>> from copilot import base64_encode
>>> base64_encode(b"test")
b'dGVzdA=='

>>> from copilot import base64_decode
>>> base64_decode(base64_encode(b"test"))
b'test'

>>> from copilot import quicksort
>>> quicksort([5,2,3,4])
[2, 3, 4, 5]
```

You can also output the code of imported functions like so:
```python
>>> from copilot import say_hello
>>> print(say_hello._code)
def say_hello():
    print("Hello, World!")
```

## How do I get an authentication token?

To obtain an authentication token to the Copilot API, you will need a GitHub
account with access to Copilot.

`copilot-importer` has an authentication CLI built-in, which you can use to
fetch your copilot authentication token. To star the authentication process
after installing `copilot-importer`, simply run
```shell
copilot-auth
```
OR
```shell
python -m copilot
```
OR
```shell
python -c "from copilot.authflow import run; run()"
```

Once you have started the authentication flow, you will be prompted to enter
a device authorization code to
[https://github.com/login/device](https://github.com/login/device).

After entering the correct code, you will be asked to authorize
_GitHub for VSCode_ to access your account. This is expected, as the Copilot
API is only accessible to the VSCode plugin.

Once approved, you should see a Copilot access token printed to the terminal.

Example:
```console
$ copilot-auth
Initializing a login session...
YOUR DEVICE AUTHORIZATION CODE IS: XXXX-XXXX
Input the code to https://github.com/login/device in order to authenticate.

Polling for login session status until 2021-07-17T17:26:01.618386
Polling for login session status: authorization_pending
Polling for login session status: authorization_pending
Successfully obtained copilot token!


YOUR TOKEN: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX:XXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
EXPIRES AT: 2021-07-17T21:21:39

You can add the token to your environment e.g. with
export GITHUB_COPILOT_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX:XXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```


## Credits

- Inspiration taken from
  [stack-overflow-import](https://github.com/drathier/stack-overflow-import)
- GitHub for providing GitHub Copilot.
- [molenzwiebel](https://github.com/molenzwiebel) for working out the Copilot
  API and helping with the code.
- [akx](https://github.com/akx) for giving a quick review of the code.
