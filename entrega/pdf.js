const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
(async () => { const [html, pdf] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage();
  await p.goto("file://" + require("path").resolve(html)); await p.pdf({ path: pdf, format: "Letter", printBackground: true }); await b.close(); console.log("pdf ok", pdf); })();
