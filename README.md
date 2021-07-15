# Copilot Importer

Why write code when you can import it directly from GitHub Copilot?

## What is Copilot Importer?

The `copilot` python module will dynamically generate any function imported
by leveraging the GitHub Copilot service.

## How do I use Copilot Importer?

You can install copilot-importer via pip (e.g. `pip install copilot-importer`).

Additionally and importantly, you need a GitHub Copilot API token. If you have
access to GitHub Copilot, you can find your token from (TODO: ADD TOKEN INSTRUCTIONS).

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

## Credits

- Inspiration taken from
  [stack-overflow-import](https://github.com/drathier/stack-overflow-import)
- GitHub for providing GitHub Copilot
- [molenzwiebel](https://github.com/molenzwiebel) for working out the copilot
  API and most of the code
- [akx](https://github.com/akx) for giving a quick review of the code
