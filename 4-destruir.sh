#!/usr/bin/env bash
# Paso 4: borra todo lo creado para que la cuenta no siga gastando créditos.
source "$(dirname "$0")/scripts/comun.sh"
[ -d "${TF_DATA_DIR:-$RAIZ/infra/.terraform}" ] || tf init -input=false >/dev/null

titulo "Esto borra la red, los servidores y la base de datos de $REGION"
if [ "${1:-}" != "--si" ]; then
  read -r -p "Escribe SI para confirmar: " R
  [ "$R" = "SI" ] || { echo "Cancelado: no se borró nada."; exit 0; }
fi

tf destroy -input=false -auto-approve

titulo "Verificando que no quedó nada"
QUEDAN="$(aws resourcegroupstaggingapi get-resources --tag-filters Key=Proyecto,Values=vlans-aws \
  --query 'length(ResourceTagMappingList)' --output text)"
if [ "$QUEDAN" = "0" ]; then listo "No queda ningún recurso del proyecto: la cuenta ya no gasta créditos."
else aviso "Aún aparecen $QUEDAN recursos (algunos tardan unos minutos en desaparecer). Vuelve a ejecutar ./4-destruir.sh --si"; fi
