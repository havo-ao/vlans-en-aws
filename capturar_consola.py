#!/usr/bin/env python3
"""Abre la consola de AWS con una sesión temporal (solo lectura por defecto) y guarda capturas, sin contraseñas."""
import json, os, subprocess, sys, urllib.parse, urllib.request

REGION = "us-east-2"
cred = json.loads(subprocess.run(["aws", "sts", "get-federation-token", "--name", "capturas", "--duration-seconds", "3600",
    "--policy-arns", "arn=arn:aws:iam::aws:policy/" + os.environ.get("POLITICA", "ReadOnlyAccess"), "--output", "json"], capture_output=True, text=True, check=True).stdout)["Credentials"]
sesion = json.dumps({"sessionId": cred["AccessKeyId"], "sessionKey": cred["SecretAccessKey"], "sessionToken": cred["SessionToken"]})
tok = json.load(urllib.request.urlopen("https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=" + urllib.parse.quote_plus(sesion)))["SigninToken"]
destino = f"https://{REGION}.console.aws.amazon.com/vpcconsole/home?region={REGION}"
login = "https://signin.aws.amazon.com/federation?Action=login&Issuer=capturas&Destination=" + urllib.parse.quote_plus(destino) + "&SigninToken=" + tok
json.dump({"login": login, "paginas": json.load(open(sys.argv[1]))}, open("/tmp/.consola_sesion.json", "w"))
