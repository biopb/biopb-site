# Getting started

This page gets you from nothing to your first agent-driven analysis. For a friendly,
click-through installer tailored to your operating system (including Windows), use the
[interactive install guide](https://biopb.org/install.html). The steps below are the short
version.

## 1. Install biopb

For the impatient, here's the command:

```bash
curl -fsSL https://biopb.org/install.sh | bash
```

For the rest, go to the [interactive install guide](https://biopb.org/install.html) and follow either route.

!!! tip "What does `curl … | bash` do?"
    It downloads the setup script and runs it. You can read exactly what it does first — it's
    plain text at [biopb.org/install.sh](https://biopb.org/install.sh) (and
    [install.ps1](https://biopb.org/install.ps1) for Windows).

## 2. Open your agent and ask

That's it. Open your AI agent and ask it, in plain language, to do something:

> "Connect to biopb and report status"

Your agent launches biopb on its own whenever it needs it, opens a napari viewer, runs the
work, and shows you the result. You watch it happen and can adjust the layers by hand.

See [Working with your agent](working-with-agents.md) for more examples of what to ask.

## 3. What LLM should you use?

If the agent workflow is new to you, you should first check what LLM you are using.
In opencode (and many other agent tools), you type:

> /model

to see current and other available models.

!!! tip "Use a free model or not"
    You may see models being labeled **free**. Great! Try all of them to get a
    feeling of the workflow. But know that they may not be **smart** enough to do a
    complicated task. A few **smart** models that we have tested and are happy with:

    - `glm-5`: many vendors, e.g., [opencode go](https://opencode.ai/go)
    - `opus` series: subscription at [anthropic](https://anthropic.com)
    - `gpt-5.5`: subscription via [codex](https://openai.com/codex)
    
## Having trouble?

Head to [Troubleshooting](troubleshooting.md), or reach out via
[Help & community](help.md).
