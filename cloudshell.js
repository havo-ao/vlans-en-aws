// Maneja AWS CloudShell con Playwright: escribe comandos y guarda capturas. Uso: node cloudshell.js pasos.json
const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright"); const fs = require("fs");
(async () => {
  const { login } = JSON.parse(fs.readFileSync("/tmp/.consola_sesion.json")); fs.unlinkSync("/tmp/.consola_sesion.json");
  const pasos = JSON.parse(fs.readFileSync(process.argv[2])); const dir = process.argv[3] || "capturas/06_cloudshell";
  fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 1.5, locale: "es-ES" });
  const p = await ctx.newPage();
  await p.goto(login, { waitUntil: "domcontentloaded", timeout: 60000 }); await p.waitForTimeout(7000);
  await p.goto("https://us-east-2.console.aws.amazon.com/cloudshell/home?region=us-east-2", { waitUntil: "domcontentloaded" }); await p.waitForTimeout(25000);
  for (const [texto, x, y] of [["Cerrar", 1097, 682], ["Rechazar", 1335, 745]]) {
    const bt = p.getByRole("button", { name: texto, exact: true }).first();
    if (await bt.isVisible().catch(() => false)) await bt.click().catch(() => {}); else await p.mouse.click(x, y);
    await p.waitForTimeout(2500);
  }
  await p.screenshot({ path: `${dir}/00_inicio.png` });
  const t = { focus: async () => { await p.mouse.click(600, 420); } };
  for (const [nombre, cmd, espera, hasta] of pasos) {
    await t.focus(); await p.keyboard.type(cmd, { delay: 8 }); await p.keyboard.press("Enter");
    const fin = Date.now() + espera * 1000; let n = 0;
    while (Date.now() < fin) { await p.waitForTimeout(15000); n++;
      if (n % 8 === 0) { await p.screenshot({ path: `${dir}/${nombre}_t${n}.png` }); await p.mouse.move(700 + n, 500); } }
    await p.screenshot({ path: `${dir}/${nombre}.png` }); console.log("ok", nombre, new Date().toTimeString().slice(0, 8));
  }
  await b.close();
})();
