import ast
import http.client
import json
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_loader
from typing import Any, Dict, List

TOKEN = os.environ.get("GITHUB_COPILOT_TOKEN")


def get_suggestion(file: str, snippet: str, stops: List[str]) -> Dict[Any, Any]:
    conn = http.client.HTTPSConnection("copilot.githubassets.com")
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
    conn.request(
        "POST",
        "/v1/engines/github-py-stochbpe-cushman-pii/completions",
        payload,
        headers,
    )
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        raise RuntimeError(
            "Copilot returned an error:\n"
            f"Status: {response.status}\n"
            "Response:\n\n"
            f"{data}",
        )
    return json.loads(data.decode("utf-8"))


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
            exec(
                lines[0]
                + "\n    "
                + "\n".join([f"import {i}" for i in imports])
                + "\n"
                + "\n".join(lines[1:]),
                globals(),
                loc,
            )
            return loc[name](*args)
        except NameError as e:
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
