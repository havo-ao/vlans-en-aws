#!/usr/bin/env python3
"""Genera el manual en dos formatos desde un solo contenido: MANUAL.md (para GitHub) y manual.html (para el PDF)."""
import base64, html, pathlib, re

AQUI = pathlib.Path(__file__).parent
REPO = "https://github.com/havo-ao/vlans-en-aws"
B = []
def h2(t): B.append(("h2", t))
def h3(t): B.append(("h3", t))
def p(t): B.append(("p", t))
def ol(*i): B.append(("ol", i))
def ul(*i): B.append(("ul", i))
def cmd(c, nota=None): B.append(("cmd", c, nota))
def img(f, pie): B.append(("img", f, pie))
def nota(tipo, t): B.append(("nota", tipo, t))      # tipo: ojo | bien | dato
def tabla(cab, filas): B.append(("tabla", cab, filas))

# ------------------------------------------------------------------ contenido
p("Este manual te lleva de la mano, desde no tener nada hasta tener funcionando en Amazon Web Services (AWS) una red dividida en tres capas aisladas, con una aplicación real encima, y luego a borrarla. **No necesitas saber de redes ni de programación, ni instalar nada en tu computador:** todo se hace desde el navegador, copiando y pegando cuatro comandos.")

h2("Lo que vas a construir")
img("img/00_arquitectura.jpg", "La red que vas a crear: tres capas, cada una en su propia subred, y cada una solo acepta a la anterior.")
p("En una red tradicional los equipos se separan con VLANs. En AWS no hay VLANs: se separan con **subredes**, **tablas de ruteo** y **reglas**. Vas a crear una red privada (VPC) con tres capas:")
ul("**Capa pública:** la única que se ve desde Internet. Tiene el balanceador, que recibe a los visitantes.",
   "**Capa de aplicación:** un servidor privado con una pequeña aplicación de reservas. Solo acepta al balanceador.",
   "**Capa de datos:** una base de datos MySQL. Solo acepta a la aplicación y no tiene ninguna salida a Internet.")

h2("Antes de empezar")
tabla(["Necesitas", "Para qué"],
      [["Un computador con navegador", "Chrome, Edge, Firefox o Safari. Sirve Windows, Mac o Linux."],
       ["Un correo electrónico", "Será el usuario de tu cuenta de AWS."],
       ["Un celular", "AWS envía un código para verificar tu identidad."],
       ["Una tarjeta de crédito o débito", "AWS la pide para verificar la identidad. Con el plan gratuito no te cobra."],
       ["Unos 40 minutos", "15 para la cuenta, 10 para desplegar, 10 para mirar y probar, y 5 para borrar."]])
nota("ojo", "**La red consume créditos mientras esté encendida.** En nuestra cuenta gastó unos 20 USD de crédito en tres días. El plan gratuito trae 100 USD de crédito y no cobra dinero real, pero cuando termines haz siempre el **paso 7 (borrar todo)**.")

h2("Paso 1 · Crea tu cuenta de AWS")
ol("Entra a **https://aws.amazon.com/es/free/** y haz clic en **Crear una cuenta gratuita**.",
   "Escribe tu correo y un nombre para la cuenta (por ejemplo `redes-vlans`). AWS te envía un código al correo: escríbelo.",
   "Crea una contraseña. Guárdala bien: es la del dueño de la cuenta.",
   "Cuando te pregunte por el plan, elige **Gratuito** (Free). Es el que da los 100 USD de crédito y no cobra.",
   "Llena tus datos de contacto (tipo de cuenta **Personal**) y los de la tarjeta.",
   "Verifica tu celular con el código que te llega por mensaje o llamada.",
   "En el plan de soporte elige **Básico (gratis)**.",
   "Espera el correo de bienvenida de AWS. Puede tardar unos minutos.")
img("img/01_capa_gratuita.png", "La página de inicio. El botón «Crear una cuenta gratuita» abre el formulario de registro.")
img("img/03_correo.png", "El correo que confirma que la cuenta está lista: plan gratuito, 100 USD de crédito y seis meses de vigencia.")

h2("Paso 2 · Entra a la consola y abre CloudShell")
p("La **consola** es la página desde la que se maneja AWS. **CloudShell** es una ventana de comandos que vive dentro de la consola: ya trae todo instalado y ya sabe quién eres, así que no hay que configurar nada.")
ol("Entra a **https://console.aws.amazon.com/** e inicia sesión con tu correo y tu contraseña (opción *usuario raíz*).",
   "Si aparece una ventana de bienvenida, ciérrala con la X.",
   "Haz clic en el ícono de CloudShell: es un cuadrito con los símbolos `>_`, arriba a la derecha (también está abajo a la izquierda, con el nombre **CloudShell**).",
   "La primera vez muestra un mensaje de bienvenida: haz clic en **Cerrar**.",
   "Espera a que aparezca una línea que termina en `$`. Ahí es donde vas a pegar los comandos.")
img("img/04_consola.png", "La consola de AWS. El ícono de CloudShell está arriba a la derecha y abajo a la izquierda.")
img("img/05_cloudshell.png", "CloudShell listo: la línea que termina en $ espera tus comandos.")
nota("dato", "**Cómo pegar un comando:** cópialo de este manual, haz clic dentro de la ventana negra y pega con `Ctrl + V` (en Mac, `Cmd + V`). Luego presiona `Enter`. Pega **un comando a la vez** y espera a que vuelva a aparecer el `$` antes de pegar el siguiente.")

h2("Paso 3 · Descarga el proyecto")
p("Este comando trae a CloudShell todos los archivos del proyecto y entra en su carpeta:")
cmd("git clone https://github.com/havo-ao/vlans-en-aws.git && cd vlans-en-aws")
img("img/06_clonar.png", "Al terminar, la línea de comandos muestra el nombre de la carpeta: vlans-en-aws.")

h2("Paso 4 · Prepara las herramientas")
p("Este comando instala Terraform (el programa que construye la red) y revisa que tu cuenta pueda crear la red en la región donde estás:")
cmd("./1-preparar.sh")
img("img/07_preparar.png", "Tres chulos verdes: Terraform instalado, cuenta reconocida y región apta.")
nota("ojo", "**Si aparece una X roja que dice que la cuenta no permite crear redes en esa región:** en las cuentas nuevas suele funcionar una sola región. Mira la dirección de la página en el navegador: la región es el texto del tipo `us-east-2`. Prueba abrir la consola en otra región cambiando ese texto en la dirección (por ejemplo `us-east-2`, que es Ohio y es la que nos sirvió), abre CloudShell otra vez y repite los pasos 3 y 4.")

h2("Paso 5 · Despliega la red")
p("Este es el comando principal. Crea los 46 elementos de la red, espera a que la aplicación arranque y te muestra su dirección:")
cmd("./2-desplegar.sh")
p("Tarda **entre 7 y 10 minutos**. Verás pasar muchas líneas: es Terraform contando lo que va creando. Lo que más demora es la base de datos. **No cierres la pestaña.**")
img("img/08_desplegar.png", "Al final aparece «Apply complete! Resources: 46 added» y la dirección de tu aplicación.")
ol("Copia la dirección que aparece en color (empieza por `http://` y termina en `amazonaws.com`).",
   "Ábrela en una pestaña nueva del navegador.",
   "Crea una reserva: escribe un nombre, elige una sala y una fecha, y haz clic en **Reservar**.")
img("img/09_aplicacion.png", "La aplicación funcionando. Arriba muestra por dónde pasó tu visita: balanceador, servidor de aplicación y base de datos, cada uno en su capa.")
nota("dato", "Si la página muestra un error 502 o no carga, espera un minuto y recarga: el servidor todavía está terminando de arrancar la aplicación.")

h2("Paso 6 · Comprueba que las capas están aisladas")
p("Este comando hace siete intentos de conexión, desde distintos lugares, y te dice si cada uno salió como debía:")
cmd("./3-probar.sh")
img("img/10_probar.png", "Los siete intentos. [OK] significa que la red se comportó como se diseñó.")
tabla(["Intento", "Qué debe pasar", "Por qué"],
      [["1. De fuera al balanceador", "Responde", "Es la única puerta abierta al público"],
       ["2. De fuera a la base de datos", "Sin respuesta", "No tiene dirección pública ni ruta a Internet"],
       ["3. De fuera a la aplicación", "Sin respuesta", "Solo se llega a ella por el balanceador"],
       ["4. De la capa pública a la base de datos", "Sin respuesta", "La base de datos solo acepta a la aplicación"],
       ["5. De la capa pública a la aplicación", "Sin respuesta", "La aplicación solo acepta al balanceador"],
       ["6. De la aplicación a la base de datos", "Abierto", "Es el único origen permitido"],
       ["7. De la aplicación a Internet", "Sale con otra dirección", "Sale a través del NAT; nadie puede entrar por ahí"]])
h3("Si quieres ver la red en la consola (opcional)")
ol("En la barra de búsqueda de la consola escribe **VPC** y entra.",
   "Haz clic en **Sus VPC** y luego en la que se llama `vlans-vpc`.",
   "Baja hasta **Mapa de recursos**: verás las seis subredes y hacia dónde sale cada una.")
img("img/11_mapa.png", "El mapa de recursos: las subredes públicas salen a Internet, las de aplicación al NAT y las de datos a ninguna parte.")

h2("Paso 7 · Borra todo")
p("Cuando termines, borra la red para que la cuenta no siga gastando créditos:")
cmd("./4-destruir.sh")
p("Te pide confirmación: escribe `SI` (en mayúsculas) y presiona `Enter`. Tarda **unos 5 minutos**; lo que más demora es borrar la base de datos.")
img("img/12_destruir.png", "«Destroy complete! Resources: 46 destroyed»: se borraron los 46 elementos.")
img("img/13_verificacion.png", "La verificación final: el chulo verde confirma que no quedó nada encendido.")
nota("bien", "Si al final aparece el chulo verde **«No queda ningún recurso del proyecto»**, terminaste. Puedes cerrar la pestaña.")

h2("Si algo sale mal")
tabla(["Qué pasó", "Qué hacer"],
      [["CloudShell se cerró o se quedó en blanco", "Vuelve a abrirlo, escribe `cd vlans-en-aws` y repite el comando en el que ibas. No se pierde lo que ya se creó."],
       ["Se cerró a mitad del paso 5", "Abre CloudShell, escribe `cd vlans-en-aws` y vuelve a ejecutar `./2-desplegar.sh`: continúa donde quedó."],
       ["Dice «Permission denied» al ejecutar un paso", "Estás fuera de la carpeta. Escribe `cd ~/vlans-en-aws` e inténtalo de nuevo."],
       ["La región no sirve (X roja en el paso 4)", "Cambia de región como se explica en el paso 4."],
       ["La aplicación muestra error 502", "Espera uno o dos minutos y recarga la página."],
       ["Quieres empezar de cero", "Ejecuta `./4-destruir.sh`, espera el chulo verde y repite desde el paso 5."],
       ["No estás seguro de si quedó algo encendido", "Ejecuta `./4-destruir.sh --si`. Si no hay nada, lo dice."]])

h2("Qué hace cada comando por dentro")
p("Los cuatro comandos son atajos. Por dentro usan Terraform, una herramienta que lee archivos de texto donde está descrita la red y la crea en AWS.")
tabla(["Comando", "Lo que hace realmente", "Archivos que usa"],
      [["`./1-preparar.sh`", "Descarga Terraform, verifica su integridad y pregunta a AWS si la región permite crear la red", "`scripts/comun.sh`"],
       ["`./2-desplegar.sh`", "`terraform init` (descarga el conector de AWS) y `terraform apply` (crea los 46 recursos)", "`infra/red.tf`, `seguridad.tf`, `datos.tf`, `computo.tf`"],
       ["`./3-probar.sh`", "Ejecuta comandos dentro de los servidores con AWS Systems Manager y compara cada resultado con lo esperado", "`pruebas/pruebas.py`"],
       ["`./4-destruir.sh`", "`terraform destroy` y luego busca si quedó algún recurso del proyecto", "El estado guardado en `infra/`"]])
p("Si quieres leer cómo está escrita la red, abre la carpeta `infra/` del repositorio. Lo esencial está en tres ideas:")
ul("**Subredes** (`red.tf`): cada capa es un rango de direcciones distinto, 10.0.1.x, 10.0.11.x y 10.0.21.x.",
   "**Tablas de ruteo** (`red.tf`): la capa pública sale a Internet, la de aplicación solo sale por el NAT y la de datos no sale.",
   "**Reglas encadenadas** (`seguridad.tf`): cada capa solo acepta conexiones de la capa anterior, en un puerto concreto.")

h2("Palabras que aparecen en el manual")
tabla(["Palabra", "Qué significa"],
      [["AWS", "Amazon Web Services: la nube de Amazon, donde se alquilan servidores y redes por horas."],
       ["VPC", "*Virtual Private Cloud*, nube privada virtual: tu red privada dentro de AWS."],
       ["Subred", "Un trozo de la red con su propio rango de direcciones. Hace el papel de la VLAN."],
       ["Balanceador", "Recibe a los visitantes y los pasa a la aplicación."],
       ["NAT", "*Network Address Translation*: deja que los servidores privados salgan a Internet sin que nadie pueda entrar a ellos."],
       ["Terraform", "Programa que crea la red a partir de archivos de texto."],
       ["CloudShell", "La ventana de comandos que viene dentro de la consola de AWS."],
       ["Región", "El lugar del mundo donde AWS crea tus recursos. `us-east-2` es Ohio, en Estados Unidos."],
       ["Crédito", "Saldo de regalo del plan gratuito. Lo que consumes se descuenta de ahí, no de tu tarjeta."]])
p(f"Todo el proyecto está en **{REPO}**. Autores: Juan José Ascuntar y Andrés Felipe Cañón · Redes de Datos II · Universidad El Bosque.")

TITULO = "Manual: monta una red segmentada en AWS desde cero"
SUB = "VLANs en AWS · paso a paso, sin instalar nada y sin conocimientos previos"

# ------------------------------------------------------------------ Markdown
ICONO = {"ojo": "⚠️", "bien": "✅", "dato": "💡"}
md = [f"# {TITULO}", "", f"*{SUB}*", ""]
for b in B:
    k = b[0]
    if k == "h2": md += [f"## {b[1]}", ""]
    elif k == "h3": md += [f"### {b[1]}", ""]
    elif k == "p": md += [b[1], ""]
    elif k == "ol": md += [f"{i}. {x}" for i, x in enumerate(b[1], 1)] + [""]
    elif k == "ul": md += [f"- {x}" for x in b[1]] + [""]
    elif k == "cmd": md += ["```bash", b[1], "```", ""]
    elif k == "img": md += [f"![{b[2]}]({b[1]})", "", f"*{b[2]}*", ""]
    elif k == "nota": md += [f"> {ICONO[b[1]]} {b[2]}", ""]
    elif k == "tabla":
        md += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])] + ["| " + " | ".join(f) + " |" for f in b[2]] + [""]
(AQUI / "MANUAL.md").write_text("\n".join(md), encoding="utf-8")

# ------------------------------------------------------------------ HTML (→ PDF)
def ih(t):
    out = []
    for part in re.split(r"(\*\*.+?\*\*|`.+?`|\*.+?\*)", t):
        if part.startswith("**"): out.append(f"<b>{html.escape(part[2:-2])}</b>")
        elif part.startswith("`"): out.append(f"<code>{html.escape(part[1:-1])}</code>")
        elif part.startswith("*") and len(part) > 2: out.append(f"<i>{html.escape(part[1:-1])}</i>")
        else: out.append(html.escape(part))
    return re.sub(r"(https?://[^\s<]+?)(?=[.,)]?(\s|$|<))", r'<a href="\1">\1</a>', "".join(out))
def dato(f):
    r = AQUI / f; tipo = "image/jpeg" if r.suffix == ".jpg" else "image/png"
    return f"data:{tipo};base64," + base64.b64encode(r.read_bytes()).decode()

CSS = """@page{size:Letter;margin:1.7cm 1.8cm}
body{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;font-size:11pt;line-height:1.5;color:#1b2430;margin:0}
.portada{background:#232F3E;color:#fff;border-radius:14px;padding:26px 30px;margin-bottom:16px}
.portada h1{font-size:23pt;line-height:1.15;margin:0 0 6px}.portada h1 span{color:#FF9900}.portada p{margin:0;color:#c9d3e2;font-size:11.5pt}
.portada .a{margin-top:14px;font-size:9.8pt;color:#a9b6c9}
h2{font-size:15pt;color:#232F3E;border-bottom:3px solid #FF9900;padding-bottom:3px;margin:22px 0 9px;page-break-after:avoid}
h3{font-size:11.8pt;color:#232F3E;margin:14px 0 5px;page-break-after:avoid}
p{margin:5px 0}ol,ul{margin:5px 0 8px;padding-left:22px}li{margin:3px 0}
code{font-family:Menlo,Consolas,monospace;font-size:9.6pt;background:#eef0f2;padding:0 4px;border-radius:3px}
.cmd{background:#0d1117;color:#e6edf3;border-radius:9px;padding:11px 14px;margin:8px 0;font-family:Menlo,Consolas,monospace;font-size:10.4pt;page-break-inside:avoid;border-left:6px solid #FF9900}
.cmd .et{display:block;font-family:-apple-system,Arial,sans-serif;font-size:8pt;letter-spacing:1px;text-transform:uppercase;color:#FF9900;margin-bottom:3px;font-weight:700}
figure{margin:9px 0 12px;page-break-inside:avoid;text-align:center}
figure img{max-width:100%;max-height:8.6cm;border:1px solid #c9d0d6;border-radius:8px}
figcaption{font-size:9.2pt;color:#5b6675;margin-top:3px}
.nota{border-radius:8px;padding:8px 12px;margin:9px 0;font-size:10.4pt;page-break-inside:avoid;border-left:6px solid}
.nota.ojo{background:#fff4e5;border-color:#e07b00}.nota.bien{background:#eef9f0;border-color:#1a7f37}.nota.dato{background:#eef4ff;border-color:#2f6fd0}
table{border-collapse:collapse;width:100%;font-size:9.8pt;margin:7px 0 10px;page-break-inside:avoid}
th{background:#232F3E;color:#fff;text-align:left;padding:5px 8px}td{padding:5px 8px;border-bottom:1px solid #d5dbdb;vertical-align:top}
a{color:#0b5cad;text-decoration:none}"""
H = [f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{TITULO}</title><style>{CSS}</style></head><body>",
     f"<div class='portada'><h1>Manual: monta una red segmentada en <span>AWS</span> desde cero</h1><p>{SUB}</p>"
     "<div class='a'>Juan José Ascuntar · Andrés Felipe Cañón — Redes de Datos II · Universidad El Bosque · Noviembre de 2026</div></div>"]
for b in B:
    k = b[0]
    if k == "h2": H.append(f"<h2>{ih(b[1])}</h2>")
    elif k == "h3": H.append(f"<h3>{ih(b[1])}</h3>")
    elif k == "p": H.append(f"<p>{ih(b[1])}</p>")
    elif k in ("ol", "ul"): H.append(f"<{k}>" + "".join(f"<li>{ih(x)}</li>" for x in b[1]) + f"</{k}>")
    elif k == "cmd": H.append(f"<div class='cmd'><span class='et'>Copia y pega en CloudShell</span>{html.escape(b[1])}</div>")
    elif k == "img": H.append(f"<figure><img src='{dato(b[1])}'><figcaption>{ih(b[2])}</figcaption></figure>")
    elif k == "nota": H.append(f"<div class='nota {b[1]}'>{ih(b[2])}</div>")
    elif k == "tabla": H.append("<table><tr>" + "".join(f"<th>{ih(x)}</th>" for x in b[1]) + "</tr>" + "".join("<tr>" + "".join(f"<td>{ih(c)}</td>" for c in f) + "</tr>" for f in b[2]) + "</table>")
H.append("</body></html>")
(AQUI / "manual.html").write_text("\n".join(H), encoding="utf-8")
print("MANUAL.md y manual.html generados ·", sum(1 for b in B if b[0] == "img"), "imágenes")
