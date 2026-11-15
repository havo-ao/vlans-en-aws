const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(`file://${__dirname}/manual.html`);
  await p.pdf({ path: `${__dirname}/Manual_VLANs_en_AWS.pdf`, format: "Letter", printBackground: true, displayHeaderFooter: true, headerTemplate: "<div></div>",
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#777">Manual · VLANs en AWS · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: { top: "1.7cm", bottom: "1.7cm", left: "1.8cm", right: "1.8cm" } });
  await b.close(); console.log("pdf ok"); })();
