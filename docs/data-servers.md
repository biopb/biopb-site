# Data (tensor) servers

A **tensor server** serves your microscopy data over the network as uniform, lazy, chunked
arrays. The default biopb install runs one locally for you, so most people never have to
think about this page. Read on when you want to serve data from a shared store, an HPC node,
or a lab data machine.

## What it does

- **Reads many formats** — OME-Zarr, OME-TIFF, HDF5, CZI, LIF, ND2, TIFF, DICOM, NIfTI, and
  more — and presents them all as uniform tensors. Clients never deal with proprietary
  formats.
- **Lazy, chunked, near-zero-copy** access over [Apache Arrow
  Flight](https://arrow.apache.org/docs/format/Flight.html), so you can work with images far
  larger than your RAM.
- **A queryable catalog** of available data sources, discovered by scanning directories you
  point it at.
- Optionally serves a **built-in web viewer** alongside the data API (http://127.0.0.1:8814).

## Connecting

The Data Browser (and your agent) resolve the server URL in this order:

1. the `BIOPB_TENSOR_URL` environment variable (with `BIOPB_TENSOR_TOKEN` for auth),
2. the saved `tensor_browser.server_url` in your config,
3. the default `grpc://localhost:8815`.

To point biopb at an existing server, set the environment variable before launching your
agent or napari:

```bash
export BIOPB_TENSOR_URL=grpc://lab-data.example.org:8815
export BIOPB_TENSOR_TOKEN=your_secure_token
```

### Auto-starting a local server

If the connection fails, the URL is local, and the `biopb` command-line tool is on your
`PATH`, the Data Browser offers to start a local server for you (`biopb server start`). If
`biopb` isn't installed, that offer is skipped — install the full biopb system, or point
`BIOPB_TENSOR_URL` at a server that's already running.

## Deploying your own

The simplest way to run a server is the published Docker image:

```bash
docker run -d --rm \
    --name biopb-tensor \
    -p 8814:8814 -p 8815:8815 \
    -v /path/to/your/data:/data \
    -e BIOPB_TENSOR_TOKEN=your_secure_token \
    jiyuuchc/biopb-tensor-server:latest
```

- Port **8815** is the gRPC/Flight data API; port **8814** serves the optional web viewer.
- The `-v` mount makes a directory of data available; it's scanned to discover sources.
- `BIOPB_TENSOR_TOKEN` sets the access token (see [Security](#security)).

For multiple data sources, metadata overrides, live directory monitoring, and HPC
(Singularity/SLURM) deployment, configure the server with a TOML file and see the
[tensor-server documentation on GitHub](https://github.com/biopb/biopb/tree/main/biopb-tensor-server).

## Command-line tools

The standard install also gives you a `biopb` command (from the SDK) for managing and
diagnosing servers from a terminal. Run `biopb --help`, or `biopb <command> --help`, for the
full options — the essentials:

**Manage a local server**

```bash
biopb server start      # start the local tensor server as a background daemon
biopb server status     # is it running, and where?
biopb server stop
biopb server restart
```

**Diagnose a running server** (works against any server, local or remote — pass
`--server <url>` for a non-default one):

```bash
biopb tensor query      # list the data sources and tensors a server is serving
biopb tensor metadata   # inspect a source's metadata and tensor descriptors
biopb tensor stats      # min / max / mean for a tensor
biopb version           # show the installed biopb version
```

`biopb tensor query` is the quickest way to confirm a server is reachable and see what data
it exposes.

## Security

!!! warning "Transport is unencrypted by default"
    Only deploy a tensor server on **localhost or a trusted intranet**.

- **Token authentication** protects both the data API and the web viewer. If you don't set
  `BIOPB_TENSOR_TOKEN`, the server generates a random one — view it with
  `docker logs biopb-tensor`.
- **No encryption by default.** For untrusted networks, put a reverse proxy (e.g. Nginx) in
  front to terminate TLS, or bind to localhost only
  (`-p 127.0.0.1:8814:8814 -p 127.0.0.1:8815:8815`) and reach it over an SSH tunnel.
- A **dev/bypass mode** disables token enforcement for local development — don't use it on a
  shared machine.

See [Configuration](configuration.md) for more details on how to configure your data server.
