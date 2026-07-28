/**
 * Privacy-friendly page views via GoatCounter (no cookies).
 * Dashboard: https://offsecguard.goatcounter.com/
 *
 * One-time setup (owner):
 *   1. https://www.goatcounter.com/signup
 *   2. Create site code exactly: offsecguard
 *   3. Allow host: zhanguoxingzhe.github.io
 */
(() => {
  const CODE = "offsecguard";
  const s = document.createElement("script");
  s.async = true;
  s.dataset.goatcounter = `https://${CODE}.goatcounter.com/count`;
  s.src = "https://gc.zgo.at/count.js";
  document.head.appendChild(s);
})();
