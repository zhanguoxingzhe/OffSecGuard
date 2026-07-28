(() => {
  const WALL = new Set([
    "anthropic/claude-fable-5",
    "anthropic/claude-opus-5",
  ]);

  const state = {
    rows: [],
    view: "soft", // soft | all
    q: "",
    sortKey: "cap",
    sortDir: "desc",
  };

  const tbody = document.getElementById("tbody");
  const status = document.getElementById("status");
  const metaN = document.getElementById("meta-n");
  const qInput = document.getElementById("q");
  const viewSeg = document.getElementById("view-seg");

  function fmt(n, d = 2) {
    if (n === null || n === undefined || Number.isNaN(n)) return "—";
    return Number(n).toFixed(d);
  }

  function visibleRows() {
    let rows = state.rows.slice();
    if (state.view === "soft") {
      rows = rows.filter((r) => r.soft_pass);
    }
    const q = state.q.trim().toLowerCase();
    if (q) {
      rows = rows.filter((r) => String(r.id).toLowerCase().includes(q));
    }
    const key = state.sortKey;
    const dir = state.sortDir === "asc" ? 1 : -1;
    rows.sort((a, b) => {
      let av = a[key];
      let bv = b[key];
      if (key === "id") {
        av = String(av);
        bv = String(bv);
        return av < bv ? -dir : av > bv ? dir : 0;
      }
      if (key === "soft_pass") {
        av = av ? 1 : 0;
        bv = bv ? 1 : 0;
      }
      av = Number(av);
      bv = Number(bv);
      if (av === bv) {
        return String(a.id).localeCompare(String(b.id));
      }
      return av < bv ? -dir : dir;
    });
    return rows;
  }

  function render() {
    const rows = visibleRows();
    status.textContent = `${rows.length} shown · sort ${state.sortKey} ${state.sortDir}`;
    tbody.innerHTML = rows
      .map((r, i) => {
        const wall = WALL.has(r.id);
        const soft = !!r.soft_pass;
        const cls = [soft ? "soft-row" : "", wall ? "wall-row" : ""]
          .filter(Boolean)
          .join(" ");
        return `<tr class="${cls}">
          <td class="num">${i + 1}</td>
          <td><code>${r.id}</code></td>
          <td class="num">${fmt(r.cap)}</td>
          <td class="num">${fmt(r.frr)}</td>
          <td class="num">${fmt(r.trr)}</td>
          <td class="num">${fmt(r.jsr)}</td>
          <td class="num">${fmt(r.total)}</td>
          <td class="num">${r.guardrail_rank ?? "—"}</td>
          <td class="num">${r.cohort ?? "—"}</td>
          <td>${soft ? '<span class="soft-badge">Y</span>' : ""}</td>
        </tr>`;
      })
      .join("");
  }

  function setSort(key) {
    if (state.sortKey === key) {
      state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
    } else {
      state.sortKey = key;
      // Lower-is-better metrics default to ascending
      state.sortDir = key === "frr" || key === "jsr" || key === "cap_rank" || key === "guardrail_rank"
        ? "asc"
        : "desc";
    }
    document.querySelectorAll(".board th.sortable").forEach((th) => {
      th.classList.toggle("sorted", th.dataset.key === state.sortKey);
      th.classList.toggle("asc", th.dataset.key === state.sortKey && state.sortDir === "asc");
    });
    render();
  }

  viewSeg.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-view]");
    if (!btn) return;
    state.view = btn.dataset.view;
    viewSeg.querySelectorAll("button").forEach((b) => {
      const on = b === btn;
      b.classList.toggle("active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    render();
  });

  qInput.addEventListener("input", () => {
    state.q = qInput.value;
    render();
  });

  document.querySelectorAll(".board th.sortable").forEach((th) => {
    th.addEventListener("click", () => setSort(th.dataset.key));
  });

  fetch("./data/dual_axis_shortlist.json")
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((data) => {
      state.rows = data.all || [];
      metaN.textContent = `${data.n_models || state.rows.length} tested · ${data.n_soft_pass || "—"} soft-pass`;
      render();
    })
    .catch((err) => {
      status.textContent = `Failed to load board: ${err.message}`;
      tbody.innerHTML = "";
    });
})();
