# Configuration

Most of biopb is configured for you by the installer. This page collects the settings you're
most likely to touch — chiefly which data server to use and where things live on disk.

## Environment variables

| Variable | What it controls |
|----------|------------------|
| `BIOPB_TENSOR_URL` | The [data server](data-servers.md) to connect to (e.g. `grpc://localhost:8815`). Used as a fallback when no control plane answers. |
| `BIOPB_TENSOR_TOKEN` | Access token for the data server (see [Security](data-servers.md#security)). |
| `BIOPB_CONTROL_HOST` | Host the control plane binds and clients look for (default `127.0.0.1`). |
| `BIOPB_CONTROL_PORT` | Port the control plane listens on (default `8813`). |
| `BIOPB_BASE_PORT` | **Containers only.** Base port inside the container (default `8810`); the ports below are derived from it. |

Set these before launching your agent or napari, for example:

```bash
export BIOPB_TENSOR_URL=grpc://lab-data.example.org:8815
export BIOPB_TENSOR_TOKEN=your_secure_token
```

When running a **tensor server** yourself, additional variables (`BIOPB_TENSOR_TOKEN`,
`CONFIG_FILE`) apply on the server side — see [Data (tensor) servers](data-servers.md).

## Ports

| Port | Used by |
|------|---------|
| `8813` | **Control plane** — the web origin you visit (dashboard, viewer, admin) |
| `8814` | Tensor server HTTP sidecar (API only; the control plane proxies it) |
| `8815` | Tensor server gRPC / Arrow Flight data API |
| `50051` | Algorithm server gRPC (default) |

`8813` is the one to remember — everything you open in a browser goes through it. The
control plane reverse-proxies the other two, so on a normal install you never visit `8814`
directly.

If a default port is already in use — common on shared machines or HPC nodes — point
`BIOPB_TENSOR_URL` at the server that's already running rather than starting a new one. In a
**container**, shift all three at once with `BIOPB_BASE_PORT` (web origin becomes `BASE+3`,
sidecar `BASE+4`, gRPC `BASE+5`).

## File locations

Paths below are for Linux and macOS.

### Config files

Both files live side by side in `~/.config/biopb/`, but they are **never merged** — each is
owned and validated by exactly one process:

- **Data server config:** `~/.config/biopb/biopb.json` — settings for the tensor server (data
  sources, ports, cache). Override the path with the `CONFIG_FILE` env var. A legacy
  `biopb.toml` is still read; if both exist, the JSON wins and the TOML is ignored with a
  warning.
- **Client / MCP config:** `~/.config/biopb/mcp-config.json` — settings for the napari client
  and agent bridge. This is also where the Data Browser remembers the last server URL
  (`tensor_browser.server_url`), so you don't have to set it every time.

!!! note "Don't confuse `mcp-config.json` with `mcp.json`"
    `mcp-config.json` is biopb's own settings file. `mcp.json` is the *client-definition*
    file your agent reads to learn how to launch biopb — a different file, written by
    `biopb agents register`.

### Logs and cache

- **Session (kernel) logs:** `~/.local/share/biopb-mcp/log/sessions/<session-id>.log` — output
  from the kernel that runs your agent's code and hosts the napari viewer. Each agent session
  gets its own file. Check here if a session misbehaves.
- **Data server logs:** `~/.local/share/biopb/log/` — when the data plane fails to start, the
  full server output is written here. Check it for the underlying error. You can also read it
  from the dashboard at [http://127.0.0.1:8813/logs](http://127.0.0.1:8813/logs).
- **On-disk cache:** Data servers lean heavily on caching to achieve fast zero-copy data transfer.
  But you can delete these files if you no longer need the server or want to start from scratch.

## What's inside the config files

### Data server — `biopb.json`

The local tensor server reads a JSON file. A minimal one points it at a directory of data
(directories are scanned recursively):

```json
{
  "server": { "host": "127.0.0.1", "port": 8815 },
  "sources": [
    { "url": "/data", "monitor": true, "alias": "my-data" }
  ]
}
```

!!! warning "Always set `server.host` explicitly"
    If you hand-write this file and leave `server.host` out, it defaults to `0.0.0.0` —
    binding publicly. The control plane refuses to start that way without a token, so set
    `"host": "127.0.0.1"` for a normal local setup. (The installer writes it for you.)

Give a source a friendly name with `alias`. A source's id is derived from its resolved URL,
so the same data always maps to one catalog entry — an explicit `sources.source_id` is
ignored with a warning.

You can declare multiple sources, override metadata per source, and enable live directory
monitoring. See [github source](https://github.com/biopb/biopb/tree/main/biopb-tensor-server) 
for the full reference.

### Client / MCP — `mcp-config.json`

The client config is a nested JSON file. It's deep-merged with the built-in defaults, so you
only need to include the keys you want to change. Every section sits at the **top level** of
the file. The entries most users touch:

| Key | Default | What it does |
|-----|---------|--------------|
| `tensor_browser.server_url` | `grpc://localhost:8815` | Which data server to connect to, when no control plane answers. |
| `services.process_image_servers` | `[]` | List of [algorithm server](algorithm-servers.md) URLs to expose to your agent, e.g. `["grpc://localhost:50051"]`. |
| `dask.scheduler` | `"distributed"` | Compute mode: `"distributed"` (multi-process), `"threads"`, or `"synchronous"`. |
| `dask.num_workers` | `0` | Worker processes for local compute; `0` lets dask pick (~CPU count). |
| `dask.memory_limit` | `"auto"` | Per-worker memory cap, e.g. `"4G"`. |
| `dask.address` | `""` | Connect to an external dask scheduler instead of spinning up a local cluster. |
| `dask.cache_budget` | `"1G"` | Cluster-wide chunk-cache budget, split across workers. |
| `transport.display_mode` | `"auto"` | `"auto"`, `"visible"`, or `"headless"` (run without opening a napari window). |

For example, to register an algorithm server:

```json
{
  "services": {
    "process_image_servers": ["grpc://localhost:50051"]
  }
}
```

An unknown or out-of-range value is never fatal: biopb warns and falls back to the default,
so a typo degrades rather than breaks your session.

There are many more advanced keys (operation timeouts, gRPC limits, pyramid building, kernel
watchdog) that most users never need to touch; the defaults are sensible. You can also ask
your agent to edit `config.json` for you instead of editing it by hand.

## See also

- [Troubleshooting](troubleshooting.md) for what to do when a setting doesn't take effect or
  a server won't start.
