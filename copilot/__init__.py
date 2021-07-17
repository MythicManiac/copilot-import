import ast
import json
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_loader
from typing import Any, Dict, List

import requests

TOKEN = os.environ.get("GITHUB_COPILOT_TOKEN")
COPILOT_API_URL = (
    "https://copilot.githubassets.com"
    "/v1/engines/github-py-stochbpe-cushman-pii/completions"
)


def get_suggestion(file: str, snippet: str, stops: List[str]) -> Dict[Any, Any]:
    payload = json.dumps(
        {
            "prompt": f"// Language: python\n// Path: {file}\n{snippet}",
            "max_tokens": 200,
            "temperature": 0.2,
            "top_p": 1,
            "n": 1,
            "logprobs": 2,
            "stop": stops,
            "stream": False,
        },
    )
    headers = {
        "OpenAI-Intent": "copilot-ghost",
        "OpenAI-Organization": "github-copilot",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        COPILOT_API_URL,
        data=payload,
        headers=headers,
    )
    if response.status_code != 200:
        raise RuntimeError(
            "Copilot returned an error:\n"
            f"Status: {response.status_code}\n"
            "Response:\n\n"
            f"{response.content}",
        )
    return json.loads(response.text)


def get_fn(name: str) -> str:
    args = get_suggestion(file=f"{name}.py", snippet=f"def {name}", stops=["):\n"])[
        "choices"
    ][0]["text"]
    func_start = f"def {name}{args}):\n"

    code = get_suggestion(
        file=f"{name}.py",
        snippet=func_start,
        stops=["\n\n\n", "\ndef ", "\nif "],
    )["choices"][0]["text"]

    full_code = func_start + code

    try:
        block_ast = ast.parse(full_code)

        if len(block_ast.body) == 1:
            return full_code
        else:
            return "\n".join(full_code.split("\n")[: block_ast.body[1].lineno - 1])
    except Exception:
        raise ImportError("Copilot's plane crashed :(")


def wrap_fn(name: str):
    source = get_fn(name)
    imports = []

    def wrapper(*args):
        try:
            loc = {}
            lines = source.split("\n")

            signature = lines[0]
            # TODO: Detect what indentation copilot generated for us
            #       seems to be a fairly consistent 4 so that'll do for now
            import_block = "\n".join([f"    import {i}" for i in imports])
            body = "\n".join(lines[1:])

            function_code = f"{signature}\n{import_block}\n{body}"

            exec(function_code, globals(), loc)
            return loc[name](*args)
        except NameError as e:
            # In case there's a name error, attempt to re-run the code with the
            # missing name added to imports first. In other words this should
            # solve some cases where copilot forgets to add appropriate imports.
            missing_name = e.args[0].split("'")[1]

            if missing_name in imports:
                raise NameError(
                    f"Copilot source references a missing value '{missing_name}'",
                )
            else:
                imports.append(missing_name)
                return wrapper(*args)
        except ModuleNotFoundError as e:
            raise ImportError(
                "Copilot source references a missing value that is also not a module",
            ) from e

    wrapper._code = source

    return wrapper


class CopilotImporter(MetaPathFinder, Loader):
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = spec_from_loader(fullname, cls, origin="hell")
        spec.__license__ = "copilot l0l"
        spec._url = "https://copilot.github.com"
        return spec

    @classmethod
    def create_module(cls, spec):
        """Create a built-in module"""
        foo = wrap_fn(spec.name.split(".")[-1])
        foo.__spec__ = spec
        return foo

    @classmethod
    def exec_module(cls, module=None):
        """Exec a built-in module"""
        pass

    @classmethod
    def get_code(cls, fullname):
        return None

    @classmethod
    def get_source(cls, fullname):
        return None

    @classmethod
    def is_package(cls, fullname):
        return False


def install():
    sys.meta_path.append(CopilotImporter())
