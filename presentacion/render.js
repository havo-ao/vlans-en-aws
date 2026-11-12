// Renderiza cada diapositiva a PNG para revisarla (todos los pasos visibles).
const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const n = +process.argv[2] || 21, solo = process.argv[3] ? process.argv[3].split(",").map(Number) : null;
  for (let i = 1; i <= n; i++) { if (solo && !solo.includes(i)) continue;
    await p.goto(`file://${__dirname}/VLANs_en_AWS.html?todo#${i}`); await p.reload(); await p.waitForTimeout(900);
    await p.screenshot({ path: `${__dirname}/revision/s${String(i).padStart(2, "0")}.jpg`, type: "jpeg", quality: 70 }); }
  await b.close(); console.log("render ok"); })();
