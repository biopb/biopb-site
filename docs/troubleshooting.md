# Troubleshooting

Fixes for the snags people hit most often. If none of these help, see
[Help & community](help.md).

## The agent can't connect to a tensor server

The Data Browser resolves the server URL in this order:

1. `BIOPB_TENSOR_URL` (with `BIOPB_TENSOR_TOKEN`),
2. the saved `tensor_browser.server_url` in your config,
3. the default `grpc://localhost:8815`.

If you expected a remote server, make sure `BIOPB_TENSOR_URL` is set **before** you launch
your agent or napari:

```bash
export BIOPB_TENSOR_URL=grpc://lab-data.example.org:8815
export BIOPB_TENSOR_TOKEN=your_secure_token
```

## A local server won't auto-start

When the connection fails and the URL is local, the browser offers to start a local server
for you — but only if the `biopb` command-line tool is on your `PATH`. If `biopb` **isn't**
installed, that offer is skipped silently. Either:

- install the full [biopb](https://github.com/biopb/biopb) system, or
- point `BIOPB_TENSOR_URL` at a server that's already running.

## A server starts but then fails

When auto-start fails, the browser shows the underlying cause inline, and the **full server
output is written to `~/.local/share/biopb/logs/`** — check there for the real error. Common
causes:

### Port already in use

Most likely on a shared machine or HPC node where another user already holds the default gRPC
port (`8815`). Either:

- point at the existing server instead of starting a new one — set `BIOPB_TENSOR_URL` (with
  `BIOPB_TENSOR_TOKEN`), or
- give your own server a free port. For the **containerized / HPC** server, set
  `BIOPB_BASE_PORT=9000` (HTTP becomes `BASE+4`, gRPC `BASE+5`). For a **local
  `biopb server start`**, put a distinct gRPC `port` in your JSON config and pass a free
  `--web-port`, then point clients at it with `BIOPB_TENSOR_URL`.

Each user gets a private on-disk cache (`%TEMP%\biopb-cache-<username>` on Windows,
`<tmp>/biopb-cache-<uid>` elsewhere) with its own lock, so multiple users running their own
server on the same node don't collide. See [Running on Windows and shared
machines](data-servers.md#running-on-windows-and-shared-machines) for the full per-user setup.

### Server started but not reachable in time

Startup exceeded the timeout. Check the server log for the real error, then try connecting
again once it's up.

## Algorithm server problems

- **No GPU / CUDA errors** — confirm an NVIDIA driver (>= 525) and the [NVIDIA Container
  Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  are installed, and that you launched the container with `--gpus=all`.
- **Connection refused** — check the published port (`-p 50051:50051`) and that the agent is
  pointed at the right host and port.

See [Algorithm servers](algorithm-servers.md) for the full run reference.

## Still stuck?

Open an [issue on GitHub](https://github.com/biopb/biopb/issues) with the error message you
saw, or ask on the [image.sc forum](https://forum.image.sc/). See [Help &
community](help.md).
