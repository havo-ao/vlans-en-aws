// Ejecuta comandos reales y guarda su salida como imagen tipo terminal (el ID de cuenta se enmascara).
const { chromium } = require("/Users/acanon/lab3_k6/node_modules/playwright");
const { execSync } = require("child_process");
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const mask = s => s.replace(/3472\d{4}(\d{4})/g, "3472••••$1");
const run = c => { try { return execSync("( " + c + " ) 2>&1", { encoding: "utf8", shell: "/bin/zsh" }); } catch (e) { return (e.stdout || "") + (e.stderr || ""); } };
const SHOTS = [
  ["01_herramientas_instaladas", ["aws --version", "terraform version | head -1"]],
  ["02_identidad_usuario", ["aws sts get-caller-identity", "aws configure get region"]],
  ["03_plan_gratuito_creditos", ["aws freetier get-account-plan-state --region us-east-1"]],
  ["04_region_permitida_ohio", ["aws ec2 describe-vpcs --region us-east-1 2>&1 | fold -s -w 112 | head -5", "aws ec2 describe-vpcs --region us-east-2 --query 'Vpcs[].{VPC:VpcId,CIDR:CidrBlock,PorDefecto:IsDefault}' --output table"]],
  ["05_red_por_defecto_ohio", ["aws ec2 describe-subnets --query 'Subnets[].{Subred:SubnetId,Zona:AvailabilityZone,CIDR:CidrBlock,IPpublica:MapPublicIpOnLaunch}' --output table", "aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text"]],
];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1000, height: 400 }, deviceScaleFactor: 2 });
  for (const [name, cmds] of SHOTS) {
    const body = cmds.map(c => `<span class="p">$ ${esc(c)}</span>\n${esc(mask(run(c))).trimEnd()}`).join("\n\n");
    const stamp = new Date().toLocaleString("es-CO", { timeZone: "America/Bogota" });
    await p.setContent(`<body style="margin:0;background:#0d1117"><div style="font:12px Menlo,monospace;color:#8b949e;padding:10px 18px 0">Terminal — ${stamp}</div>
      <pre style="font:13.5px/1.5 Menlo,monospace;color:#e6edf3;margin:0;padding:10px 18px 18px;white-space:pre-wrap">${body}</pre><style>.p{color:#7ee787;font-weight:bold}</style></body>`);
    await p.screenshot({ path: `capturas/02_cli/${name}.png`, fullPage: true });
    console.log("ok", name);
  }
  await b.close();
})();
