# How biopb fits together

You only ever talk to your **agent** and watch the **napari** window. But it helps to know
what's underneath — especially once you start working with bigger data or shared servers.

biopb is built around a simple idea: Give the AI agent resources and tools, then **ask the agent to write an image analysis program specifically tailored to your data**.

!!! note "The rationale"
    Traditional image analysis platforms, e.g., Fiji, rely on a curated set of
    **plugins** written by human developers. However, writing a universally
    applicable plugin is hard, even when the underlying algorithm is solid,
    because the real data in research is highly variable and continuously evolving.
    The biopb project is an experiment to see whether using AI to generate **custom** programs on-the-fly works better on scientific data.

## The four pieces

```
        You  ⇄  AI agent
                  │
                  ▼
          napari viewer  ── you watch & edit ──►  You
          (Data Browser + MCP bridge)
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
   Data plane           Compute plane
   (tensor server)      (algorithm servers)
   moves image data     run models (Cellpose, …)
```

### Your AI agent

The agent (Claude Code, OpenCode, Cursor, or Hermes) is what you talk to. Instead of clicking
through menus, you describe what you want and the agent writes and runs the analysis code. It
can pull data, run trained models, and present results — all by operating the live napari
session for you.

Crucially, the agent isn't limited to a fixed menu of buttons. It works in a real Python
environment with your data and algorithms pre-wired in, so any analysis you can express in
plain language — filtering, measurements, region properties, spatial statistics — is fair
game.

### Napari + Data Browser

[napari](https://napari.org) is the image viewer. The **Data Browser** plugin (part of
`biopb-mcp`) lets you and your agent browse and open data together. You can tweak a layer
by hand and the agent can read it back — it's a shared canvas, not a headless batch job.

See [working with napari](using-napari.md) for details.

### The data (tensor) plane

The **tensor server** owns "where the pixels live and how they move." It reads whatever
microscopy format your lab has — OME-Zarr, OME-TIFF, HDF5, CZI, LIF, ND2, TIFF, and more —
and serves it as uniform, **lazy, chunked** arrays over [Apache Arrow
Flight](https://arrow.apache.org/docs/format/Flight.html). "Lazy" means pixels are fetched
only as needed, so your agent can work with images far larger than your computer's RAM.

The default install runs a tensor server locally for you. See
[Data (tensor) servers](data-servers.md) to connect to or deploy your own.

!!! note
    Under the hood biopb uses `dask.array` to represent all image data, and spins up a local
    dask cluster for the agent to use. This is why your agent can run some serious
    computation, instead of being just a cute demo toy. You can even hook up a
    distributed dask cluster, if your institute has one, to really run some intensive
    computations.

### The compute (algorithm) plane

**Algorithm servers** own "what algorithm runs." Each one wraps a specialized algorithm, often
a trained machine learning model, e.g., Cellpose for pixel-perfect cell segmentation, behind
the same simple interface. Biopb ship these as containers, so they can be run on dedicated
machines, e.g., one with a GPU. Because data and compute are separate, an algorithm server
can pull its input pixels straight from the data plane and write results back, so even big-image
analyses never have to round-trip through your laptop.

See [Algorithm servers](algorithm-servers.md) to run one.

## Why split data and compute?

Bioimage analysis has two very different costs: **moving big images** and **running models on
a GPU**. Keeping them separate means each can scale on its own, multiple algorithm servers
can share one data store, and large analyses can chain together — segment, then measure, then
filter — with the pixels streaming through the data plane instead of through you.

## Who runs what

biopb is designed for **personal or small-lab** use, on your own machine or a trusted lab
network. The simplest setup is everything-on-localhost (the default install). As you grow,
you can move the data server onto a shared store and the algorithm servers onto a GPU box,
and point your client at them. For untrusted networks, put a reverse proxy (TLS, auth) in
front of the servers — see the [security notes](data-servers.md#security) on the data-server
page.
