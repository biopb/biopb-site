# Algorithm servers

**Algorithm servers** run the heavy models — segmentation, detection, restoration — behind a
single uniform interface. Each wraps one model and ships as a Docker container, usually run on
a machine with a GPU. Your agent calls them through biopb; you generally just need one
running and reachable.

## Available pre-built servers

biopb publishes ready-to-run images:

| Image | Model | Use |
|-------|-------|-----|
| `jiyuuchc/cellpose` | [Cellpose Cyto3](https://cellpose.com) | General cell/nucleus segmentation |
| `jiyuuchc/cellpose-sam` | [Cellpose-SAM](https://cellpose.com) | Segmentation with the SAM backbone |
| `jiyuuchc/ucell` | [ucell](https://github.com/jiyuuchc/ucell) | Cell segmentation |
| `jiyuuchc/unifmir` | [UNiFMIR](https://github.com/cxm12/UNiFMIR) | Universal fluorescence image restoration |

## Requirements

- An **NVIDIA GPU** with a recent driver (>= 525).
- The [NVIDIA Container
  Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html),
  so Docker containers can use the GPU.

## Running a server

```bash
# Standard: expose the gRPC port 50051
docker run --gpus=all -p 50051:50051 jiyuuchc/cellpose

# Use a different host port
docker run --gpus=all -p 8888:50051 jiyuuchc/cellpose

# Require a token to access
docker run --gpus=all -p 50051:50051 jiyuuchc/cellpose --token

# Debug mode, no token
docker run --gpus=all -p 50051:50051 jiyuuchc/cellpose --no-token --debug
```

Once it's running, update your biopb-mcp config file, i.e., $HOME/.config/biopb-mcp/biopb-mcp.json,
and change the mcp.server section:

```json
"mcp": {
  "server": {
    "url": your_server_url
  }
}
```

so your agent knows to use it. You could of course also ask your agent to change
the config file for you instead of editing by hand.

!!! warning "Transport is unencrypted (HTTP) by default"
    Run algorithm servers on a trusted network. To use TLS, put a reverse proxy (e.g. Nginx)
    in front to forward the gRPC calls.

!!! note "Common Gotha"
    If dataset is large, biopb will not send all the pixels to the algorithm server but
    just a link to the data server - but that means you need to configure your data server
    to listen for the connection. All are fine if you run everything on the same machine.
    But if you are ever setting up a distributed deployment, pay attention to which ports you are
    binding!

## Building your own

Algorithm servers are deliberately uniform: each is a thin model wrapper on a shared base, so
adding a new one is mostly "wrap a model and point it at the protocol." If your lab has a
custom model, see the
[biopb-server build docs](https://github.com/biopb/biopb-server/blob/main/BUILD.md).
