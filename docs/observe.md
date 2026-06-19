# Watching your agent (the observe page)

When your agent runs code through biopb, that code executes in a live Python kernel
with full access to your data and viewer. The **observe page** is a small web UI that
lets *you* watch what the agent runs, step in when something goes wrong, and save the
whole session as a notebook for the record.

It runs locally, on the same port as biopb, and is **on by default**.

## Why it's there

An agent is a powerful but opaque collaborator. It writes and runs real Python on your
machine — segmentations, measurements, file reads — and most of the time you only see
the results, not the work. The observe page closes that gap. It exists so you can:

- **See what's actually running.** Every `execute_code` job shows up with its source and
  its captured output, newest first — so "what did the agent just do?" is always one
  glance away.
- **Step in.** If a job hangs or heads in the wrong direction, you can interrupt that
  one job or hard-restart the whole kernel — without killing the conversation.
- **Keep a record.** One click exports the entire session as a Jupyter notebook: an
  **audit trail** of every command the agent ran and what came back (see
  [Saving a notebook (audit)](#saving-a-notebook-audit) below).

This is the same idea as the [shared canvas in napari](using-napari.md) — you and the
agent work over one session — applied to the *code* the agent runs rather than the
*images* it produces.

<!-- TODO screenshot: full observe page — header with controls + a few job rows, one expanded. -->
<figure markdown>
  ![The observe page showing recent jobs](assets/observe-overview.png)
  <figcaption>The observe page: recent <code>execute_code</code> jobs, newest first, with the kernel status and controls in the header.</figcaption>
</figure>

## Opening it

The page lives at `/observe` on biopb's local port (default `8765`):

```
http://127.0.0.1:8765/observe
```

If you're not sure of the port, ask your agent to run **`server_status`** — it reports
the observe URL (along with kernel and system health) under an **Observe** heading:

```
## Observe
  url: http://127.0.0.1:8765/observe
  mode: mounted on the MCP app (http)
```

!!! note "Local only"
    The page is bound to loopback (`127.0.0.1`) and guarded by the same Host/Origin
    checks as biopb itself. It's reachable only from your own machine — there is no
    login because there is no remote access. Don't expose biopb's port to a network.

## Reading the job list

Each row is one job the agent ran, with a status badge:

| Badge | Meaning |
|-------|---------|
| **running** | The job is executing right now. |
| **ok** | Finished successfully. |
| **error** | Raised an exception (the traceback is in the output). |
| **cancelled** | Stopped by the agent. |
| **interrupted** | Stopped by *you* from this page. |

Click a row to expand it and see the **code** that was run and its **output**. The
newest job stays expanded automatically; older jobs collapse so the page doesn't get
noisy. For a running job the output tails live as it's produced (long output is
truncated to the most recent chunk, with the full length noted). The header shows the
kernel state — `alive`, `busy`, `headless` — and refreshes every few seconds.

<!-- TODO screenshot: one job row expanded, showing the code block and its captured output. -->
<figure markdown>
  ![An expanded job showing its code and output](assets/observe-job-detail.png)
  <figcaption>Expanding a job reveals the exact code the agent ran and the output it captured.</figcaption>
</figure>

## Stepping in

Three controls live in the header:

- **Interrupt** — forces a `KeyboardInterrupt` into the *currently running* job. Use
  this when a single command is stuck (a runaway loop, a stall) but the session is
  otherwise fine. The agent sees, through its normal result, that *a user* stopped the
  job — so it won't mistake the interruption for its own logic failing.
- **Restart kernel** — hard-restarts the Python kernel. This clears **all** variables
  and napari layers, so you're asked to confirm first. Reach for it when the kernel is
  wedged badly enough that interrupting one job isn't enough.
- **⤓ Save notebook** — exports the session (covered next).

!!! tip "Interrupt the job, not the conversation"
    Interrupting or restarting from this page doesn't end your chat with the agent. The
    agent simply gets back a "stopped by user" result and you can tell it what to do
    next.

## Saving a notebook (audit)

The **⤓ Save notebook** button exports the whole recorded session as a standard Jupyter
`.ipynb` file (`biopb-mcp-session-YYYYMMDD-HHMMSS.ipynb`). This is the page's most
important feature for reproducibility and review.

The notebook is an **audit record first, a runnable script second.** It faithfully
reproduces, in order:

- a title and summary cell (when it was exported, how many jobs),
- a **bootstrap cell** that rebuilds the core namespace (`np`, `da`, the data-plane
  `client`, the compute-plane `ops`, and an empty napari `viewer`) on a best-effort
  basis, and
- **one cell per job** — the exact code the agent ran, with its captured stdout,
  results, and any error or interruption message — each headed by its job id, status,
  elapsed time, and timestamp.

That gives you a complete, shareable trail of what was done to your data: drop it next
to your results, attach it to a paper's supplement, or hand it to a colleague to review.

<!-- TODO screenshot: the exported .ipynb opened in Jupyter/VS Code — bootstrap cell + a couple of job cells with output. -->
<figure markdown>
  ![The exported audit notebook opened in Jupyter](assets/observe-notebook.png)
  <figcaption>The exported notebook: each cell is one job the agent ran, kept verbatim with its output and a header line.</figcaption>
</figure>

!!! warning "Re-running has caveats"
    The notebook is meant to *document* a session, not perfectly replay it. In-namespace
    Python variables carry across cells, but **external state is not captured**:
    tensor-server source ids and the live napari layers from the original session may not
    coincide on a fresh kernel, so cells that chain `ops` source ids or read `viewer` layers
    need the same live server (or hand edits) to run again. Cells marked `error`,
    `cancelled`, or `interrupted` are kept verbatim — re-running one may re-trigger the
    same failure, so skip or edit it. Only the most recent jobs are retained, so a very
    long session may be missing its earliest steps.

## Turning it off

The observe page is on by default. To disable it, set `mcp.observe.enabled` to `false`
in your [config file](configuration.md):

```json
{
  "mcp": {
    "observe": {
      "enabled": false
    }
  }
}
```

Two other knobs under `mcp.observe` tune it: `max_output_chars` (how much of a job's
output the detail view shows, default `20000`) and `poll_interval_ms` (how often the
page refreshes, default `3000`).
