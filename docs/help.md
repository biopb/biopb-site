# Help & community

Hit a snag, found a bug, or have a question? Here's where to go.

## Ask a question

- **[image.sc forum](https://forum.image.sc/)** — the friendly bioimaging community. Great
  for "how do I…" questions and analysis advice. No question is too basic.

## Report a problem

- **[GitHub issues](https://github.com/biopb/biopb/issues)** — for bugs and feature requests,
  including the client/plugin (`biopb-mcp`).

### Filing a good report

A little detail goes a long way:

1. **What you did** — the command or the request you gave your agent.
2. **What happened** — paste the exact error message.
3. **Logs** — when a server fails, the full output is in `~/.local/share/biopb/log/`; attach
   the relevant part. For a misbehaving agent session, the kernel log is in
   `~/.local/share/biopb-mcp/log/sessions/`.
4. **Your setup** — operating system, whether you're on localhost or a remote server, and
   (for algorithm servers) your GPU/driver.

## Source & releases

- **Source code:** [github.com/biopb](https://github.com/biopb)
- **Releases:** [biopb releases](https://github.com/biopb/biopb/releases) — the `release-v*`
  tags are the end-user ones, and what the [installer](https://biopb.org/install.html) pulls.
- **SDK package:** [`biopb` on PyPI](https://pypi.org/project/biopb) — the protocol SDK, for
  building against biopb.

!!! warning "Don't install biopb from PyPI"
    biopb's own components (`biopb-mcp`, `biopb-tensor-server`, `biopb-control`) are **not**
    published to PyPI — they reach you only as the wheel bundle the installer fetches from a
    `release-v*` GitHub release. The old `biopb-mcp` PyPI page is abandoned at a long-stale
    version; installing from it gets you something years behind. Use the
    [install guide](https://biopb.org/install.html).
