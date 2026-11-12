const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright"); const fs = require("fs");
(async () => {
  const { login, paginas } = JSON.parse(fs.readFileSync("/tmp/.consola_sesion.json")); fs.unlinkSync("/tmp/.consola_sesion.json");
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1700, height: 1500 }, deviceScaleFactor: 1.5, locale: "es-ES" });
  const p = await ctx.newPage();
  await p.goto(login, { waitUntil: "domcontentloaded", timeout: 60000 }); await p.waitForTimeout(8000);
  let primera = true;
  for (const [nombre, url] of paginas) {
    try { await p.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 }); await p.waitForTimeout(primera ? 11000 : 8000);
      if (primera) { await p.getByRole("button", { name: "Rechazar" }).first().click({ timeout: 4000 }).catch(() => {}); primera = false; await p.waitForTimeout(1200); }
      await p.screenshot({ path: `capturas/05_consola/${nombre}.png` }); console.log("ok", nombre);
    } catch (e) { console.log("FALLO", nombre, e.message.split("\n")[0]); }
  }
  await b.close();
})();
