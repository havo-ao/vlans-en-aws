# Configuración compartida por los cuatro pasos. No se ejecuta sola.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/bin:$PATH"

# En CloudShell el disco que se conserva es de 1 GB y los complementos de Terraform pesan
# unos 700 MB: se guardan en /tmp. El estado (lo que Terraform creó) sí queda en la carpeta.
if [ "${AWS_EXECUTION_ENV:-}" = "CloudShell" ]; then export TF_DATA_DIR="/tmp/vlans-terraform"; fi

REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null || true)}}"
if [ -z "$REGION" ]; then echo "No se pudo saber en qué región trabajar. Ejecuta: export AWS_REGION=us-east-2"; exit 1; fi
export AWS_REGION="$REGION" AWS_DEFAULT_REGION="$REGION" TF_VAR_region="$REGION"
[ -n "${NOMBRE:-}" ] && export TF_VAR_nombre="$NOMBRE"

titulo() { printf '\n\033[1;33m== %s ==\033[0m\n' "$1"; }
listo()  { printf '\033[1;32m✔ %s\033[0m\n' "$1"; }
aviso()  { printf '\033[1;31m✖ %s\033[0m\n' "$1"; }
tf()     { terraform -chdir="$RAIZ/infra" "$@"; }
