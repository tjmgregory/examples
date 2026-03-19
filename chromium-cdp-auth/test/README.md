# CDP Screenshot Test / Client

This is Python client using [CDP (Chrome DevTools Protocol)](https://chromedevtools.github.io/devtools-protocol/) to create a screenshot from an existing Chromium instances.

Set it up in a [Python virtual environment](https://docs.python.org/3/library/venv.html):

```console
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

Run the client with a token (required for authenticated instances):

```console
python cdp-screenshot.py https://<NAME>.<METRO>.unikraft.app <url-to-screenshot> <screenshot_filename> <token>
```

Or set the token via environment variable:

```console
export CDP_TOKEN=<token>
python cdp-screenshot.py https://<NAME>.<METRO>.unikraft.app <url-to-screenshot> <screenshot_filename>
```