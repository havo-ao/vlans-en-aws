const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(`file://${__dirname}/VLANs_en_AWS.html?todo`); await p.waitForTimeout(800);
  await p.pdf({ path: `${__dirname}/VLANs_en_AWS.pdf`, width: "1920px", height: "1080px", printBackground: true }); await b.close(); console.log("pdf ok"); })();
