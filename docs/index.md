# biopb documentation

**Open bioimage analysis, driven by your agent.**

biopb lets you analyze microscopy images by *talking to an AI agent* — Claude Code,
Claude Desktop, OpenCode, or Cursor. You ask the agent to open an image or run an analysis, and it
drives biopb for you: loading data, running segmentation and other algorithms, and showing
results in a live [napari](https://napari.org) viewer you can watch and tweak.

[Get started](getting-started.md){ .md-button .md-button--primary }
[How it fits together](concepts.md){ .md-button }

---

## What you can do

- **Open and browse large microscopy data** — OME-Zarr, OME-TIFF, CZI, LIF, ND2, and
  more — even datasets far larger than your computer's memory.
- **Do open-ended analysis in plain language.** Filtering, measurements, region properties,
  spatial statistics — your agent writes the code and you watch results appear in napari.
- **Run trained models** for segmentation and restoration (Cellpose, UNiFMIR, and
  others) without writing boilerplate.
- **Stay in control.** Image results land in the viewer; numbers and tables go to the chat;
  you decide what to save.

## Components

You mostly interact with your **agent** and the **napari** window. Everything else runs
quietly underneath:

| Piece | What it does for you |
|-------|----------------------|
| **Your AI agent** | The thing you talk to. It launches biopb and writes the analysis code. |
| **Napari + Data Browser** | The viewer where images and results appear. Your agent drives it; you can edit by hand. |
| **Dashboard** | One web page at `127.0.0.1:8813` for watching sessions, data, and logs. |
| **Control plane** | Keeps the data server running and serves the dashboard. Starts on its own. |
| **Data server** | Serves your image data, lazily, so huge files just work. |
| **Algorithm servers** | Run the dedicated algorithms — usually on a GPU machine. |

If you are just getting started, you don't need to think about the last three — the default
install wires them up for you. See [How biopb fits together](concepts.md) when you want the
full picture.

## Where to next

- **[Getting started](getting-started.md)** — install and run your first analysis.
- **[Working with your agent](working-with-agents.md)** — what to ask and how the workflow feels.
- **[Working with napari](using-napari.md)** — What do you do in the napari window.
- **[Troubleshooting](troubleshooting.md)** — fixes for the common snags.

!!! note "These docs are for end users"
    Looking for protocol internals, contributor guides, or the gRPC/Arrow Flight specs?
    Those live in the source repositories on [GitHub](https://github.com/biopb).
