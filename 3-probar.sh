#!/usr/bin/env bash
# Paso 3: lanza los siete intentos de conexión y dice si cada uno salió como debía.
source "$(dirname "$0")/scripts/comun.sh"
[ -d "${TF_DATA_DIR:-$RAIZ/infra/.terraform}" ] || tf init -input=false >/dev/null

titulo "Pruebas de aislamiento (tardan cerca de un minuto)"
cd "$RAIZ/pruebas" && SALIDA="mis_resultados.json" python3 pruebas.py
echo
listo "Resultados guardados en pruebas/mis_resultados.json"
echo "[OK] significa que la red se comportó como se diseñó: lo permitido pasa y lo demás no responde."
