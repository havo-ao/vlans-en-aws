#!/usr/bin/env python3
"""Pruebas de aislamiento: ejecuta cada intento de conexión y guarda el resultado en resultados.json."""
import json, socket, subprocess, time, urllib.request

def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout.strip()
def tf(nombre): return json.loads(sh("terraform", "-chdir=../infra", "output", "-json"))[nombre]["value"]

URL, BD, IDS, NAT = tf("url_aplicacion"), tf("bd_endpoint"), tf("ids"), tf("ip_salida_nat")
IP_BD = None

def remoto(instancia, comando):
    """Ejecuta un comando dentro de un servidor por Systems Manager (sin SSH)."""
    cid = sh("aws", "ssm", "send-command", "--instance-ids", instancia, "--document-name", "AWS-RunShellScript",
             "--parameters", json.dumps({"commands": [comando]}), "--query", "Command.CommandId", "--output", "text")
    for _ in range(30):
        time.sleep(2)
        r = json.loads(sh("aws", "ssm", "get-command-invocation", "--command-id", cid, "--instance-id", instancia, "--output", "json") or "{}")
        if r.get("Status") in ("Success", "Failed", "TimedOut", "Cancelled"):
            return (r.get("StandardOutputContent", "") + r.get("StandardErrorContent", "")).strip()
    return "sin respuesta de SSM"

def puerto(host, p): return f"timeout 5 bash -c '</dev/tcp/{host}/{p}' 2>/dev/null && echo ABIERTO || echo 'SIN RESPUESTA'"

def local_tcp(host, p):
    try: socket.create_connection((host, p), timeout=5).close(); return "ABIERTO"
    except Exception as e: return f"SIN RESPUESTA ({type(e).__name__})"

R = []
def anotar(n, origen, destino, esperado, comando, salida):
    ok = ("ABIERTO" in salida or salida.startswith("200") or salida == NAT) if esperado == "permitido" else ("SIN RESPUESTA" in salida)
    R.append(dict(n=n, origen=origen, destino=destino, esperado=esperado, comando=comando, salida=salida, cumple=ok))
    print(f"{n}. {origen} -> {destino}: {salida}  [{'OK' if ok else 'REVISAR'}]")

IP_BD = socket.gethostbyname(BD)
ip_app = IDS["ip_app"]
codigo = str(urllib.request.urlopen(URL + "/api/health", timeout=10).status)
anotar(1, "Internet", "Balanceador :80", "permitido", f"curl {URL}/api/health", codigo + " OK")
anotar(2, "Internet", f"Base de datos {IP_BD}:3306", "bloqueado", f"nc -vz -w 5 {BD} 3306", local_tcp(BD, 3306))
anotar(3, "Internet", f"Aplicación {ip_app}:8080", "bloqueado", f"nc -vz -w 5 {ip_app} 8080", local_tcp(ip_app, 8080))
anotar(4, "Subred pública", f"Base de datos {IP_BD}:3306", "bloqueado", f"</dev/tcp/{IP_BD}/3306", remoto(IDS["pruebas"], puerto(IP_BD, 3306)))
anotar(5, "Subred pública", f"Aplicación {ip_app}:8080", "bloqueado", f"</dev/tcp/{ip_app}/8080", remoto(IDS["pruebas"], puerto(ip_app, 8080)))
anotar(6, "Aplicación", f"Base de datos {IP_BD}:3306", "permitido", f"</dev/tcp/{IP_BD}/3306", remoto(IDS["app"], puerto(IP_BD, 3306)))
anotar(7, "Aplicación", "Internet (por el NAT)", "permitido", "curl https://checkip.amazonaws.com", remoto(IDS["app"], "curl -s -m 8 https://checkip.amazonaws.com"))

json.dump(dict(fecha=time.strftime("%Y-%m-%d %H:%M:%S"), url=URL, bd=BD, ip_bd=IP_BD, ip_app=ip_app, nat=NAT, pruebas=R), open("resultados.json", "w"), ensure_ascii=False, indent=1)
