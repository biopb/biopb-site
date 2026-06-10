# Configuration

Most of biopb is configured for you by the installer. This page collects the settings you're
most likely to touch — chiefly which data server to use and where things live on disk.

## Environment variables

| Variable | What it controls |
|----------|------------------|
| `BIOPB_TENSOR_URL` | The [data server](data-servers.md) to connect to (e.g. `grpc://localhost:8815`). Takes precedence over saved config. |
| `BIOPB_TENSOR_TOKEN` | Access token for the data server. |
| `BIOPB_BASE_PORT` | Base port used when starting a local server — change it to avoid a clash on a shared machine (e.g. `BIOPB_BASE_PORT=9000`). |

Set these before launching your agent or napari, for example:

```bash
export BIOPB_TENSOR_URL=grpc://lab-data.example.org:8815
export BIOPB_TENSOR_TOKEN=your_secure_token
```

When running a **tensor server** yourself, additional variables (`BIOPB_TENSOR_TOKEN`,
`CONFIG_FILE`, dev-bypass flags) apply on the server side — see
[Data (tensor) servers](data-servers.md).

## Ports

| Port | Used by |
|------|---------|
| `8815` | Tensor server gRPC / Arrow Flight data API (default) |
| `8814` | Tensor server web viewer (HTTP) |
| `50051` | Algorithm server gRPC (default) |

If a default port is already in use — common on shared machines or HPC nodes — either start
your server on a different base port with `BIOPB_BASE_PORT`, or point `BIOPB_TENSOR_URL` at
the server that's already running rather than starting a new one.

## File locations

- **Logs:** `~/.local/share/biopb/logs/` — when a local server fails to start, the full
  server output is written here. Check it for the underlying error.
- **On-disk cache:** each user gets a private cache (e.g. `/tmp/biopb-cache-<uid>`) with its
  own lock, so multiple users on the same node don't collide.
- **Saved client config:** the Data Browser remembers the last server URL
  (`tensor_browser.server_url`) so you don't have to set it every time.

## See also

- [Troubleshooting](troubleshooting.md) for what to do when a setting doesn't take effect or
  a server won't start.
