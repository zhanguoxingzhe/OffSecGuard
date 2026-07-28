(() => {
  const canvas = document.getElementById("scatter");
  if (!canvas) return;

  const HIGHLIGHT = new Set([
    "openai/gpt-5.5",
    "qwen/qwen3.7-max",
    "openai/o4-mini",
    "openai/gpt-5.4",
  ]);
  const WALL = new Set([
    "anthropic/claude-fable-5",
    "anthropic/claude-opus-5",
  ]);

  function shortName(id) {
    return id.split("/").pop();
  }

  function draw(points) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const cssW = canvas.clientWidth || 680;
    const cssH = 420;
    canvas.width = Math.floor(cssW * dpr);
    canvas.height = Math.floor(cssH * dpr);
    canvas.style.height = `${cssH}px`;
    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);

    const pad = { l: 48, r: 16, t: 18, b: 42 };
    const w = cssW - pad.l - pad.r;
    const h = cssH - pad.t - pad.b;

    const xs = points.map((p) => p.total);
    const ys = points.map((p) => p.cap);
    const xmin = Math.min(...xs) - 2;
    const xmax = Math.max(...xs) + 2;
    const ymin = Math.min(...ys) - 2;
    const ymax = Math.max(...ys) + 2;

    const x = (v) => pad.l + ((v - xmin) / (xmax - xmin)) * w;
    const y = (v) => pad.t + (1 - (v - ymin) / (ymax - ymin)) * h;

    ctx.clearRect(0, 0, cssW, cssH);
    ctx.fillStyle = "#fbfcfd";
    ctx.fillRect(0, 0, cssW, cssH);

    // grid
    ctx.strokeStyle = "#e6ebf0";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const yy = pad.t + (h * i) / 4;
      const xx = pad.l + (w * i) / 4;
      ctx.beginPath();
      ctx.moveTo(pad.l, yy);
      ctx.lineTo(pad.l + w, yy);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(xx, pad.t);
      ctx.lineTo(xx, pad.t + h);
      ctx.stroke();
    }

    // axes labels
    ctx.fillStyle = "#5c6570";
    ctx.font = "12px IBM Plex Mono, monospace";
    ctx.textAlign = "center";
    ctx.fillText("guardrail total_score →", pad.l + w / 2, cssH - 12);
    ctx.save();
    ctx.translate(14, pad.t + h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("cap_score →", 0, 0);
    ctx.restore();

    // ticks
    ctx.textAlign = "right";
    ctx.fillText(String(Math.round(ymin)), pad.l - 6, y(ymin) + 3);
    ctx.fillText(String(Math.round(ymax)), pad.l - 6, y(ymax) + 3);
    ctx.textAlign = "center";
    ctx.fillText(String(Math.round(xmin)), x(xmin), pad.t + h + 16);
    ctx.fillText(String(Math.round(xmax)), x(xmax), pad.t + h + 16);

    const labeled = [];

    function paint(p, color, r) {
      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.arc(x(p.total), y(p.cap), r, 0, Math.PI * 2);
      ctx.fill();
    }

    // rest first
    for (const p of points) {
      if (HIGHLIGHT.has(p.id) || WALL.has(p.id)) continue;
      paint(p, p.soft_pass ? "#0b6e4f99" : "#9aa3ad99", p.soft_pass ? 4.5 : 3.5);
    }
    for (const p of points) {
      if (!WALL.has(p.id)) continue;
      paint(p, "#9b2c2c", 6);
      labeled.push(p);
    }
    for (const p of points) {
      if (!HIGHLIGHT.has(p.id)) continue;
      paint(p, "#1d4f91", 6.5);
      labeled.push(p);
    }

    // labels for highlights / walls
    ctx.font = "11px IBM Plex Mono, monospace";
    ctx.textAlign = "left";
    for (const p of labeled) {
      const px = x(p.total) + 8;
      const py = y(p.cap) - 8;
      ctx.fillStyle = WALL.has(p.id) ? "#9b2c2c" : "#1d4f91";
      ctx.fillText(shortName(p.id), px, py);
    }
  }

  fetch("./data/dual_axis.json")
    .then((r) => r.json())
    .then((data) => {
      const points = data.points || [];
      draw(points);
      window.addEventListener("resize", () => draw(points));
    })
    .catch((err) => {
      const ctx = canvas.getContext("2d");
      ctx.font = "14px sans-serif";
      ctx.fillStyle = "#9b2c2c";
      ctx.fillText("Failed to load dual_axis.json", 16, 28);
      console.error(err);
    });
})();
