// Capturas para el manual: página de registro (pública) y consola (sesión temporal de solo lectura).
const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright"); const fs = require("fs");
(async () => {
  const { login } = JSON.parse(fs.readFileSync("/tmp/.consola_manual.json")); fs.unlinkSync("/tmp/.consola_manual.json");
  const b = await chromium.launch(); const d = "capturas/07_manual";
  const pub = await (await b.newContext({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1.5, locale: "es-ES" })).newPage();
  await pub.goto("https://aws.amazon.com/es/free/", { waitUntil: "domcontentloaded", timeout: 60000 }).catch(e => console.log("free:", e.message.split("\n")[0]));
  await pub.waitForTimeout(6000); await pub.screenshot({ path: `${d}/01_pagina_capa_gratuita.png` });
  await pub.goto("https://signin.aws.amazon.com/signup?request_type=register", { waitUntil: "domcontentloaded", timeout: 60000 }).catch(e => console.log("signup:", e.message.split("\n")[0]));
  await pub.waitForTimeout(9000); await pub.screenshot({ path: `${d}/02_registro.png` }); console.log("registro:", pub.url().slice(0, 80));
  const ctx = await b.newContext({ viewport: { width: 1500, height: 900 }, deviceScaleFactor: 1.5, locale: "es-ES" }); const p = await ctx.newPage();
  await p.goto(login, { waitUntil: "domcontentloaded", timeout: 60000 }); await p.waitForTimeout(7000);
  await p.goto("https://us-east-2.console.aws.amazon.com/console/home?region=us-east-2", { waitUntil: "domcontentloaded" }); await p.waitForTimeout(12000);
  await p.getByRole("button", { name: "Rechazar", exact: true }).first().click({ timeout: 5000 }).catch(() => {});
  await p.waitForTimeout(2500); await p.screenshot({ path: `${d}/03_consola_inicio.png` });
  await p.mouse.click(1420, 20); await p.waitForTimeout(2500); await p.screenshot({ path: `${d}/04_menu_cuenta.png` });
  await b.close(); console.log("ok manual");
})();
