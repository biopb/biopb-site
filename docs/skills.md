---
hide:
  - toc
---

# Skills

**Skills** are curated, reusable workflows for your agent — short recipes like
"segment nuclei", "load a tensor source", or "measure labels and export a table".
Each is a small Markdown file the agent reads on demand to follow a vetted set of
steps instead of improvising.

The agent discovers these automatically with its `find_skills` tool and reads the
matching one before starting a task; this page is the **human-browsable** view of
the same catalog. See the [skill interface design][design] for how the catalog is
built and published.

[design]: https://github.com/biopb/biopb/blob/main/biopb-mcp/docs/skill-interface.md

<div id="skills-app" data-catalog="/skills/catalog.json" markdown="0">
  <div class="skills-controls">
    <input id="skills-search" class="skills-search" type="search"
           placeholder="Search skills…" autocomplete="off"
           aria-label="Search skills by title, description, or tag">
    <div id="skills-tags" class="skills-tags" role="group" aria-label="Filter by tag"></div>
  </div>
  <p id="skills-status" class="skills-status" role="status">Loading skills…</p>
  <div id="skills-grid" class="skills-grid"></div>
</div>

<style>
#skills-app { margin-top: 1.2rem; }
.skills-controls { display: flex; flex-direction: column; gap: .7rem; margin-bottom: 1rem; }
.skills-search {
  width: 100%; box-sizing: border-box; padding: .55rem .8rem; font-size: .85rem;
  border: 1px solid var(--md-default-fg-color--lighter);
  border-radius: .4rem; background: var(--md-default-bg-color);
  color: var(--md-default-fg-color);
}
.skills-search:focus { outline: none; border-color: var(--md-accent-fg-color); }
.skills-tags { display: flex; flex-wrap: wrap; gap: .4rem; }
.skills-tag {
  font-size: .72rem; line-height: 1; padding: .34rem .6rem; cursor: pointer;
  border: 1px solid var(--md-default-fg-color--lighter);
  border-radius: 1rem; background: transparent;
  color: var(--md-default-fg-color--light); user-select: none;
}
.skills-tag[aria-pressed="true"] {
  background: var(--md-accent-fg-color); border-color: var(--md-accent-fg-color);
  color: var(--md-primary-bg-color, #fff);
}
.skills-status { font-size: .82rem; color: var(--md-default-fg-color--light); }
.skills-grid {
  display: grid; gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
}
.skill-card {
  display: flex; flex-direction: column; gap: .55rem; padding: 1rem;
  border: 1px solid var(--md-default-fg-color--lighter);
  border-radius: .5rem; background: var(--md-default-bg-color);
}
.skill-card h3 { margin: 0; font-size: .95rem; line-height: 1.3; }
.skill-card h3 a { color: var(--md-default-fg-color); }
.skill-desc { margin: 0; font-size: .82rem; line-height: 1.45; color: var(--md-default-fg-color--light); flex: 1; }
.skill-tagrow { display: flex; flex-wrap: wrap; gap: .35rem; }
.skill-tagrow span {
  font-size: .68rem; padding: .18rem .45rem; border-radius: .8rem;
  background: var(--md-accent-fg-color--transparent, rgba(37,99,214,.1));
  color: var(--md-accent-fg-color);
}
.skill-meta {
  display: flex; justify-content: space-between; align-items: baseline; gap: .5rem;
  font-size: .72rem; color: var(--md-default-fg-color--lighter);
  border-top: 1px solid var(--md-default-fg-color--lightest, rgba(0,0,0,.07));
  padding-top: .5rem;
}
.skill-meta a { font-size: .74rem; }
</style>

<script>
(function () {
  var root = document.getElementById("skills-app");
  if (!root) return;
  var catalogUrl = root.getAttribute("data-catalog") || "/skills/catalog.json";
  var searchEl = document.getElementById("skills-search");
  var tagsEl = document.getElementById("skills-tags");
  var statusEl = document.getElementById("skills-status");
  var gridEl = document.getElementById("skills-grid");

  var skills = [];
  var activeTags = new Set();

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function matches(sk) {
    var q = searchEl.value.trim().toLowerCase();
    if (q) {
      var hay = (sk.title + " " + sk.description + " " + (sk.tags || []).join(" ")).toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    if (activeTags.size) {
      // OR across selected tags: show a skill matching ANY active tag.
      var has = (sk.tags || []).some(function (t) { return activeTags.has(t); });
      if (!has) return false;
    }
    return true;
  }

  function render() {
    var shown = skills.filter(matches);
    gridEl.innerHTML = shown.map(function (sk) {
      var tags = (sk.tags || []).map(function (t) { return "<span>" + esc(t) + "</span>"; }).join("");
      var updated = sk.updated ? "updated " + esc(sk.updated) : "";
      var ver = sk.version ? "v" + esc(sk.version) : "";
      var src = sk.url
        ? '<a href="' + esc(sk.url) + '" rel="noopener">View source</a>'
        : "";
      return (
        '<article class="skill-card">' +
          "<h3>" + (sk.url ? '<a href="' + esc(sk.url) + '" rel="noopener">' + esc(sk.title) + "</a>" : esc(sk.title)) + "</h3>" +
          '<p class="skill-desc">' + esc(sk.description) + "</p>" +
          (tags ? '<div class="skill-tagrow">' + tags + "</div>" : "") +
          '<div class="skill-meta"><span>' + [ver, updated].filter(Boolean).join(" · ") + "</span>" + src + "</div>" +
        "</article>"
      );
    }).join("");
    if (!shown.length) {
      statusEl.textContent = skills.length
        ? "No skills match the current filter."
        : "No skills are published yet.";
      statusEl.style.display = "";
    } else {
      statusEl.style.display = "none";
    }
  }

  function renderTags() {
    var all = {};
    skills.forEach(function (sk) { (sk.tags || []).forEach(function (t) { all[t] = (all[t] || 0) + 1; }); });
    var names = Object.keys(all).sort();
    tagsEl.innerHTML = names.map(function (t) {
      return '<button type="button" class="skills-tag" data-tag="' + esc(t) + '" aria-pressed="false">' +
        esc(t) + " <small>(" + all[t] + ")</small></button>";
    }).join("");
    tagsEl.querySelectorAll(".skills-tag").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var t = btn.getAttribute("data-tag");
        if (activeTags.has(t)) { activeTags.delete(t); btn.setAttribute("aria-pressed", "false"); }
        else { activeTags.add(t); btn.setAttribute("aria-pressed", "true"); }
        render();
      });
    });
  }

  searchEl.addEventListener("input", render);

  fetch(catalogUrl, { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (cat) {
      skills = (cat && Array.isArray(cat.skills) ? cat.skills : [])
        .slice()
        .sort(function (a, b) { return String(a.title).localeCompare(String(b.title)); });
      renderTags();
      render();
    })
    .catch(function (e) {
      statusEl.textContent =
        "Could not load the skills catalog (" + e.message + "). " +
        "It is published to /skills/catalog.json on biopb.org.";
    });
})();
</script>
