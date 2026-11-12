const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright"); const fs = require("fs");
(async () => {
  const { login, paginas } = JSON.parse(fs.readFileSync("/tmp/.consola_sesion.json")); fs.unlinkSync("/tmp/.consola_sesion.json");
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 2100, height: 1750 }, deviceScaleFactor: 1.5, locale: "es-ES" });
  const p = await ctx.newPage();
  await p.goto(login, { waitUntil: "domcontentloaded", timeout: 60000 }); await p.waitForTimeout(8000);
  await p.goto(paginas[0][1], { waitUntil: "domcontentloaded" }); await p.waitForTimeout(11000);
  await p.getByRole("button", { name: "Rechazar" }).first().click({ timeout: 5000 }).catch(() => console.log("sin aviso de cookies"));
  await p.waitForTimeout(1500);
  const t = p.getByText("Mostrar todos los detalles").first(); const c = await t.boundingBox().catch(() => null); console.log(JSON.stringify(c));
  const y0 = 462;
  await p.screenshot({ path: "capturas/05_consola/09_mapa_de_recursos_recorte.png", clip: { x: 392, y: y0, width: 1700, height: 620 } });
  await b.close(); console.log("ok mapa");
})();
