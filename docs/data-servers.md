# Data (tensor) servers

A **tensor server** serves your microscopy data over the network as uniform, lazy, chunked
arrays. The default biopb install runs one locally for you, so most people never have to
think about this page. Read on when you want to serve data from a shared store, an HPC node,
or a lab data machine.

## What it does

- **Reads many formats** — OME-Zarr, OME-TIFF, CZI, LIF, ND2, TIFF, DICOM, NIfTI, and
  more — and presents them all as uniform tensors. Clients never deal with proprietary
  formats.
- **Lazy, chunked, near-zero-copy** access over [Apache Arrow
  Flight](https://arrow.apache.org/docs/format/Flight.html), so you can work with images far
  larger than your RAM.
- **A queryable catalog** of available data sources, discovered by scanning directories you
  point it at.
- Feeds the **built-in web viewer**, which the [control plane](concepts.md#the-control-plane)
  serves at [http://127.0.0.1:8813/viewer](http://127.0.0.1:8813/viewer).

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

You normally don't have to start anything. When your agent or the Data Browser needs data, it
asks the **control plane** to bring the data plane up if it isn't already, and the control
plane hands back the address to connect to. That's idempotent — asking twice is harmless.

Only when no control plane answers does biopb fall back to the resolution order above and
connect directly to whatever `BIOPB_TENSOR_URL` (or the saved config) points at.

## Deploying your own

The simplest way to run a server is the published Docker image:

```bash
docker run -d --rm \
    --name biopb-tensor \
    -p 8813:8813 -p 8815:8815 \
    -v /path/to/your/data:/data \
    -e BIOPB_TENSOR_TOKEN=your_secure_token \
    jiyuuchc/biopb-tensor-server:latest
```

- Port **8813** is the web origin — the dashboard, viewer, and admin pages. Port **8815** is
  the gRPC/Flight data API, for SDK clients.
- **Don't publish 8814.** The HTTP sidecar is loopback-internal; the control plane (which is
  the container's main process) proxies it for you.
- The `-v` mount makes a directory of data available; it's scanned to discover sources.
- `BIOPB_TENSOR_TOKEN` sets the access token (see [Security](#security)).
- Shift all three ports at once with `BIOPB_BASE_PORT` (default `8810`): the web origin is
  `BASE+3`, the sidecar `BASE+4`, and gRPC `BASE+5`.

For multiple data sources, metadata overrides, live directory monitoring, and HPC
(Singularity/SLURM) deployment, configure the server with a JSON file and see the
[tensor-server documentation on GitHub](https://github.com/biopb/biopb/tree/main/biopb-tensor-server).

## Command-line tools

The standard install also gives you a `biopb` command (from the SDK) for managing and
diagnosing servers from a terminal. Run `biopb --help`, or `biopb <command> --help`, for the
full options — the essentials:

**Manage the local stack**

The **control plane** owns the data plane: start it and it brings the tensor server up with
it, supervises it, and restarts it if it crashes.

```bash
biopb control start     # start the control plane + the data plane it supervises
biopb control status    # is it running, and how is the data plane doing?
biopb control stop      # complete teardown, data plane included
biopb control run       # same as start, but in the foreground
```

Or just run `biopb dashboard`, which starts the control plane if it isn't up and opens the
dashboard in your browser.

!!! warning "`biopb server start` is deprecated"
    The standalone tensor-server daemon commands (`biopb server start` / `stop` / `restart` /
    `status` / `logs`) still work but print a deprecation notice and will be removed in a
    future release. The control plane now owns the data plane — use `biopb control start` and
    `biopb control status` instead. (`biopb server cache-stats` and `biopb server
    migrate-config` are unaffected.)

!!! note "Lifecycle: the local control plane is session-bound, not persistent"
    A locally started control plane lives with your login session and is taken down when that
    session ends — Windows hard-kills session processes on logout, and modern Linux
    (systemd-logind) kills the user scope on logout regardless of `setsid`. This is by
    design: biopb does not try to keep a local stack alive past logout. If you need a tensor
    server that **survives logout** — a shared or remote server — run it persistently at the
    infrastructure level (the container/Compose service, a systemd unit, or `loginctl
    enable-linger`), not via the CLI.

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

In local mode the stack binds fixed loopback ports: `127.0.0.1:8813` (control), `:8814`
(sidecar), and `:8815` (gRPC). Two people logged in at once — including Windows **Fast User
Switching**, which is one click away — both try to bind the same ports. The control plane
**refuses to adopt a port it doesn't own**, reporting that the port is held by a process it
didn't start, rather than silently double-binding into a dead server. The second user reuses
or restarts the first. The on-disk cache is already per-user
(`%TEMP%\biopb-cache-<username>` on Windows, `<tmp>/biopb-cache-<uid>` elsewhere), so caches
never collide.

!!! warning "Loopback is not per-user isolated"
    Any local session can reach `127.0.0.1`, and local mode is **tokenless by default** — so
    on a shared machine, another logged-in user can read your data. Gate it with a token:

    ```bash
    biopb control start --token your_secure_token
    ```

    or set `BIOPB_TENSOR_TOKEN` before starting. The listeners stay on loopback; they just
    stop being open to everyone on the box. To run genuinely concurrent per-user servers, also
    give each one its own ports — a per-user JSON config with a distinct gRPC `port`, plus
    `biopb control start --web-port <p>` — and point each session's client at it with
    `BIOPB_TENSOR_URL`.

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
off first, so the stack dies and does **not** come back when you power on. "Shut down = fresh
start" isn't true on Windows; use **Restart** for a clean slate. Either way it's
session-bound (see the lifecycle note above), and you bring it back with `biopb dashboard` or
`biopb control start`.

## Security

!!! warning "Transport is unencrypted by default"
    Only deploy a tensor server on **localhost or a trusted intranet**.

biopb has **two deployment modes**. What the mode picks is the **bind address**; whether a
token is enforced is a separate choice you can make in either mode.

### Local (the default)

`biopb control start` binds every listener to loopback — control `8813`, sidecar `8814`, gRPC
`8815`. Nothing is reachable from off the machine.

By default there's no token and no unlock step: open
[http://127.0.0.1:8813/](http://127.0.0.1:8813/) and you're in. That's the right setting for a
machine only you use.

You can still **enforce a token locally** — worth doing on a machine you share, since loopback
is not per-user isolated:

```bash
biopb control start --token your_secure_token
```

The listeners stay on loopback, but now they're gated, and the browser asks you to unlock just
as it would remotely.

### Remote

`biopb control start --remote` binds the dashboard and the Flight server publicly, and a
**token is required**. Pass one with `--token` or `BIOPB_TENSOR_TOKEN`; if you don't, biopb
generates one and prints it. Tokens are 16–128 characters of `A–Z a–z 0–9 _ -` in either mode.

You authenticate by visiting the one-time URL biopb prints:

```
http://your-host:8813/?token=your_secure_token
```

The page stashes the token for the tab and strips it back out of the address bar, so it
doesn't linger in your history. In a container, the auto-generated token is in
`docker logs biopb-tensor`.

!!! note "The unsafe combination is unrepresentable"
    biopb refuses to start public-and-tokenless: `--remote` without a token exits with an
    error, and so does a config that binds publicly with no token to enforce. A public
    listener is never left unauthenticated, so you can't misconfigure your way into an open
    server by accident.

**Still no encryption.** Token or not, the transport is plaintext. For untrusted networks put
a reverse proxy (e.g. Nginx) in front to terminate TLS, or keep it loopback-only
(`-p 127.0.0.1:8813:8813 -p 127.0.0.1:8815:8815`) and reach it over an SSH tunnel.

See [Configuration](configuration.md) for more details on how to configure your data server.
