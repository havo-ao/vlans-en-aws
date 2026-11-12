#!/usr/bin/env python3
"""Consulta Docker dentro del servidor privado (por Systems Manager) y guarda la salida."""
import json, subprocess, time
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout.strip()
ID = json.loads(sh("terraform", "-chdir=../infra", "output", "-json"))["ids"]["value"]["app"]
def remoto(cmd):
    cid = sh("aws", "ssm", "send-command", "--instance-ids", ID, "--document-name", "AWS-RunShellScript",
             "--parameters", json.dumps({"commands": [cmd]}), "--query", "Command.CommandId", "--output", "text")
    for _ in range(30):
        time.sleep(2)
        r = json.loads(sh("aws", "ssm", "get-command-invocation", "--command-id", cid, "--instance-id", ID, "--output", "json") or "{}")
        if r.get("Status") in ("Success", "Failed"): return (r.get("StandardOutputContent", "") + r.get("StandardErrorContent", "")).rstrip()
CMDS = ["docker --version",
        "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}'",
        "docker images --format 'table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}'",
        "docker inspect -f 'red={{.HostConfig.NetworkMode}} reinicio={{.HostConfig.RestartPolicy.Name}}' reservas",
        "docker logs reservas 2>&1 | tail -3",
        "ss -ltnp | grep 8080 | awk '{print $1, $4, $6}'"]
res = [{"cmd": c, "out": remoto(c)} for c in CMDS]
json.dump(res, open("docker.json", "w"), ensure_ascii=False, indent=1)
for r in res: print("$", r["cmd"]); print(r["out"]); print()
