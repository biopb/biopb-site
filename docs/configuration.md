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

Paths below are for Linux and macOS.

### Config files

- **Data server config:** `~/.config/biopb/biopb.json` — settings for the local tensor
  server (data sources, ports, cache). Override the path with the `CONFIG_FILE` env var.
- **Client / MCP config:** `~/.config/biopb-mcp/config.json` — settings for the napari client
  and agent bridge. This is also where the Data Browser remembers the last server URL
  (`tensor_browser.server_url`), so you don't have to set it every time.

### Logs and cache

- **MCP kernel log:** `~/.local/share/biopb-mcp/log/kernel.log` — output from the kernel that
  runs your agent's code and hosts the napari viewer. Check here if the agent's session
  misbehaves.
- **Data server logs:** `~/.local/share/biopb/logs/` — when a local data server fails to start,
  the full server output is written here. Check it for the underlying error.
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
    { "url": "/data" }
  ]
}
```

You can declare multiple sources, override metadata per source, and enable live directory
monitoring. See [github source](https://github.com/biopb/biopb/tree/main/biopb-tensor-server) 
for the full reference.

### Client / MCP — `config.json`

The client config is a nested JSON file. It's deep-merged with the built-in defaults, so you
only need to include the keys you want to change. The entries most users touch:

| Key | Default | What it does |
|-----|---------|--------------|
| `tensor_browser.server_url` | `grpc://localhost:8815` | Which data server to connect to. The `BIOPB_TENSOR_URL` env var overrides it. |
| `mcp.services.process_image_servers` | `[]` | List of [algorithm server](algorithm-servers.md) URLs to expose to your agent, e.g. `["grpc://localhost:50051"]`. |
| `mcp.dask.scheduler` | `"distributed"` | Compute mode: `"distributed"` (multi-process), `"threads"`, or `"synchronous"`. |
| `mcp.dask.num_workers` | `0` | Worker processes for local compute; `0` lets dask pick (~CPU count). |
| `mcp.dask.memory_limit` | `"auto"` | Per-worker memory cap, e.g. `"4G"`. |
| `mcp.dask.address` | `""` | Connect to an external dask scheduler instead of spinning up a local cluster. |
| `mcp.dask.cache_budget` | `"1G"` | Cluster-wide chunk-cache budget, split across workers. |
| `mcp.transport.display_mode` | `"auto"` | `"auto"`, `"visible"`, or `"headless"` (run without opening a napari window). |

For example, to register an algorithm server:

```json
{
  "mcp": {
    "services": {
      "process_image_servers": ["grpc://localhost:50051"]
    }
  }
}
```

There are many more advanced keys (operation timeouts, gRPC limits, pyramid building, kernel
watchdog) that most users never need to touch; the defaults are sensible. You can also ask
your agent to edit `config.json` for you instead of editing it by hand.

## See also

- [Troubleshooting](troubleshooting.md) for what to do when a setting doesn't take effect or
  a server won't start.
