# Chromium CDP with Token Authentication

This example uses Chromium, a headless browser exposing a [CDP (Chrome DevTools Protocol)](https://chromedevtools.github.io/devtools-protocol/) websocket interface, with token-based authentication and persistent storage.

## Features

- **Token authentication**: All CDP requests (HTTP and WebSocket) require a valid token
- **Admin API**: Create, list, and revoke tokens via REST endpoints
- **Bootstrap token**: Set an initial admin token via environment variable
- **Persistent storage**: Token database is stored on a volume that survives restarts

## Running

1. Install the `kraft` CLI tool and a container runtime engine, for example [Docker](https://docs.docker.com/get-docker/).

1. Clone the examples repository and `cd` into the `examples/chromium-cdp-auth/` directory:

   ```console
   git clone https://github.com/unikraft-cloud/examples
   cd examples/chromium-cdp-auth/
   ```

1. Make sure to log into Unikraft Cloud by setting your token and a metro close to you.
   This guide uses `fra` (Frankfurt, DE):

   ```console
   export UKC_TOKEN=token
   export UKC_METRO=fra
   ```

1. Set a bootstrap admin token that will be used for initial setup:

   ```console
   export BOOTSTRAP_ADMIN_TOKEN=my-secret-admin-token
   ```

1. Deploy the app:

   ```console
   ./deploy.sh
   ```

   The deploy script builds an erofs root filesystem, creates a persistent volume for the token database, and deploys the instance.

## Authentication

All CDP endpoints require a valid token, passed either as:
- **Query parameter**: `?token=<TOKEN>`
- **Authorization header**: `Authorization: Bearer <TOKEN>`

The bootstrap admin token (set via `BOOTSTRAP_ADMIN_TOKEN` env var) can be used for initial setup. Use it to create additional tokens.

### Token Management API (admin only)

**Create a token:**
```console
curl -X POST https://<instance-url>/api/tokens \
  -H "Authorization: Bearer $BOOTSTRAP_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-client", "expiresInDays": 7}'
```

**List tokens:**
```console
curl https://<instance-url>/api/tokens \
  -H "Authorization: Bearer $BOOTSTRAP_ADMIN_TOKEN"
```

**Revoke a token:**
```console
curl -X DELETE https://<instance-url>/api/tokens/<token> \
  -H "Authorization: Bearer $BOOTSTRAP_ADMIN_TOKEN"
```

### Public Endpoints

- `GET /health` — health check (no auth required)

## Testing

To query the service you need to use a CDP client.
You can use the Python-based implementation in the `test/` directory:

```console
cd test/
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

Take a screenshot, passing the token as the last argument:

```console
python cdp-screenshot.py https://<instance-url> https://google.com screenshot.png <TOKEN>
```

Or set the token via environment variable:

```console
export CDP_TOKEN=<TOKEN>
python cdp-screenshot.py https://<instance-url> https://google.com screenshot.png
```

## Instance Management

List instances:
```console
kraft cloud instance list
```

Remove an instance:
```console
kraft cloud instance remove <instance-name>
```

## Learn more

- [CDP Documentation](https://chromedevtools.github.io/devtools-protocol/)
- [Unikraft Cloud's Documentation](https://unikraft.cloud/docs/)
- [Building `Dockerfile` Images with `Buildkit`](https://unikraft.org/guides/building-dockerfile-images-with-buildkit)

Use the `--help` option for detailed information on using Unikraft Cloud:

```console
kraft cloud --help
```

Or visit the [CLI Reference](https://unikraft.org/docs/cli/reference).
