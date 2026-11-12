const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:800},deviceScaleFactor:2});
await p.goto("http://vlans-balanceador-2110447132.us-east-2.elb.amazonaws.com",{waitUntil:"networkidle"});await p.waitForTimeout(1500);
await p.screenshot({path:"capturas/03_despliegue/01_aplicacion_por_balanceador.png"});await b.close();console.log("ok app");})();
