# Working with your agent

The heart of biopb is the conversation with your AI agent. This page covers what that feels
like and how to get good results.

## The workflow

1. **Open your agent.** No server to start — the agent launches biopb the first time it needs
   it, which opens a napari window.
2. **Ask in plain language.** Describe the data and what you want done with it.
3. **Watch it happen.** The agent writes and runs code; image results appear as layers in
   napari, and numbers and tables come back in the chat.
4. **Iterate.** Adjust a layer by hand, ask a follow-up, or refine the analysis. The agent
   sees the current state of the viewer and continues from there.

The agent works by a *perceive → act → verify* loop: it runs code that changes the viewer,
then looks at a screenshot to confirm the result actually looks right — the same way you
would.

## First prompt

```
"Connect to biopb and report status"
```
Why? If you are just setting up, this checks:

- whether your agent hears you and can respond
- whether the agent can connect to biopb
- whether all biopb's sub-system is running and healthy

## What to ask for real

Some examples to get a feel for it:

- *"Open `embryo.nd2`, show channel 2, and max-project over Z."*
- *"Segment the nuclei in the current image with Cellpose and count them."*
- *"Measure the area and mean intensity of each segmented cell and give me a table."*
- *"Threshold the membrane channel, clean up small objects, and overlay the result."*
- *"Connect to the tensor server at `grpc://lab-data:8815` and list what's available."*

## Division of labor

biopb deliberately keeps you in control:

- **Image results** (segmentations, overlays, projections) go to the **napari viewer**.
- **Quantitative results** (counts, measurements, tables) go to the **agent's chat**.
- **You decide what to keep** — save layers and results through napari yourself.

Trained-model algorithms (like Cellpose) run on dedicated [algorithm
servers](algorithm-servers.md) because agents can't do accurate segmentation unaided.
Everything else — the classical image processing and analysis — the agent does directly in
Python, which is what keeps the system open-ended.

## Tips

- **Name your files and channels.** "the DAPI channel" works better than "the blue one."
- **Work in steps.** Ask for one transformation, check it, then build on it.
- **Let it see.** If a result looks off, ask the agent to take a screenshot and re-check — it
  often catches and fixes the problem itself.
- **Point it at the right data.** If your images live on a remote server, tell the agent the
  [tensor server URL](data-servers.md) or set `BIOPB_TENSOR_URL` before launching.
