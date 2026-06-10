# Working with napari

[napari](https://napari.org) is the viewer where your images and analysis results appear. The
**Data Browser** is a widget that shows up on the right side of your napari window. This widget
(part of `biopb-mcp`) connects napari to a data server so you, and your agent, can browse and
open data.

## Browsing and opening data

The Data Browser connects to a [data server](data-servers.md) and lists the data
sources in this server's catalog. From there you can open a source (right click) as a napari image layer. 

Because data is **lazy**, opening a huge multi-dimensional image does not read all pixels into memory. Instead,
data streams in as you scroll through Z, time, or channels, and only the planes you actually view
are fetched.

## A shared canvas with your agent

The viewer you're looking at is the **same session your agent drives**. When the agent runs a
segmentation, the result appears as a new layer in front of you. You can:

- adjust contrast, colormaps, and visibility,
- edit labels or draw shapes by hand,
- and ask the agent to read your edits back and keep going.

Image results land here in the viewer; numbers and tables go to the agent's chat. **You**
decide what becomes a saved file — use napari's normal save/export to keep a layer or result.

## Doing things yourself

You don't have to go through the agent for everything. The Data Browser and napari work as
a normal viewer, so you can open data, pan and zoom, and inspect layers directly whenever you
like. The agent is there for the analysis you'd rather describe than click through.

!!! note "The detection/processing widgets are developer tools"
    The napari that comes with biopb also ships a couple of algorithm widgets. These are useful
    for people who want to test their own deployment of [algorithm servers](algorithm-servers.md) — for
    most users these can be ignored safely.