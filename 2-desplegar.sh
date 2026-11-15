#!/usr/bin/env bash
# Paso 2: crea toda la red (46 recursos, unos 7 minutos) y espera a que la aplicación responda.
source "$(dirname "$0")/scripts/comun.sh"

titulo "Preparando Terraform (descarga el conector de AWS)"
tf init -input=false | tail -3

titulo "Creando la red en $REGION: tarda unos 7 minutos, no cierres la ventana"
tf apply -input=false -auto-approve

URL="$(tf output -raw url_aplicacion)"
titulo "Esperando a que la aplicación arranque (1 a 2 minutos)"
for i in $(seq 1 40); do
  if [ "$(curl -s -m 5 -o /dev/null -w '%{http_code}' "$URL/api/health")" = "200" ]; then break; fi
  printf '.'; sleep 10
done; echo

listo "Red desplegada. Abre esta dirección en el navegador:"
printf '\n   \033[1;36m%s\033[0m\n\n' "$URL"
echo "Siguiente paso:  ./3-probar.sh     Cuando termines:  ./4-destruir.sh"
