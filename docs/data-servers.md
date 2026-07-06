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
(Singularity/SLURM) deployment, configure the server with a JSON file and see the
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

!!! note "Lifecycle: the local daemon is session-bound, not persistent"
    A daemon started with `biopb server start` lives with your login session and is
    taken down when that session ends — Windows hard-kills session processes on
    logout, and modern Linux (systemd-logind) kills the user scope on logout
    regardless of `setsid`. This is by design: biopb does not try to keep a local
    daemon alive past logout. If you need a tensor server that **survives logout** —
    a shared or remote server — run it persistently at the infrastructure level
    (the container/Compose service, a systemd unit, or `loginctl enable-linger`),
    not via `biopb server start`. Any `setsid`/detach belongs in that wrapper, not
    in the CLI.

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

## Running on Windows and shared machines

A local daemon is a per-user process bound to fixed loopback ports. A handful of platform
quirks — most of them Windows-specific — matter when several people log into the same machine,
or when you expect a server to outlive your session.

### Fixed loopback port, no per-user isolation

The daemon binds `127.0.0.1:8815` (gRPC) and `127.0.0.1:8814` (web). Two people logged in at
once — including Windows **Fast User Switching**, which is one click away — both try to bind
the same ports. biopb **detects the collision** and refuses to start a second daemon on a port
that's already taken (instead of silently double-binding into a dead server), so the second
user just reuses or restarts the first. The on-disk cache is already per-user
(`%TEMP%\biopb-cache-<username>` on Windows, `<tmp>/biopb-cache-<uid>` elsewhere), so caches
never collide.

Loopback is **not** per-user isolated, though: any local session can reach a server on
`127.0.0.1`. On a shared machine, **set `BIOPB_TENSOR_TOKEN`** so another logged-in user can't
read your data. To run genuinely concurrent per-user servers, give each one its own ports — a
per-user JSON config with a distinct gRPC `port`, plus `biopb server start --web-port <p>` —
and point each session's client at it with `BIOPB_TENSOR_URL`.

### Don't run the daemon as a Windows service to "survive logout"

It's a trap. Windows services run in **session 0**, which:

- **can't display the napari GUI** (session-0 isolation), and
- resolves `%USERPROFILE%` / `Path.home()` / `.config` to the **service account's** profile,
  not yours — so config, logs, and the cache land in the wrong place — and **can't see your
  mapped drives**.

If you genuinely need a server that outlives any login session, run it on a separate always-on
host or in a container (see [Deploying your own](#deploying-your-own)) and connect to it with
`BIOPB_TENSOR_URL` — don't try to make your workstation daemon persistent as a session-0
service.

### Point the server at UNC paths, not mapped drive letters

Windows drive-letter mappings (`Z:\`) are **per-logon-session**: they're torn down at logout
and are invisible to other sessions and to services. Give the server **UNC paths**
(`\\server\share\data`) instead — they don't depend on a session's drive map. (UNC also avoids
a race if you ever autostart the server: a mapped drive may not be mounted before the server
scans for data, so it would find nothing.)

### "Shut down" still logs you off (Fast Startup)

Windows **Fast Startup** turns "Shut down" into a hybrid hibernate — but it logs your session
off first, so the daemon dies and does **not** come back when you power on. "Shut down = fresh
start" isn't true on Windows; use **Restart** for a clean slate. Either way the daemon is
session-bound (see the lifecycle note above), and you bring it back with `biopb server start`.

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
