#!/usr/bin/env bash
# Paso 1: instala Terraform y comprueba que la cuenta permite crear la red en esta región.
source "$(dirname "$0")/scripts/comun.sh"
VERSION="1.17.2"

titulo "Instalando Terraform $VERSION"
if terraform version 2>/dev/null | grep -q "v$VERSION"; then
  listo "Terraform ya estaba instalado"
else
  case "$(uname -s)-$(uname -m)" in
    Linux-x86_64) P=linux_amd64 ;; Linux-aarch64) P=linux_arm64 ;;
    Darwin-arm64) P=darwin_arm64 ;; Darwin-x86_64) P=darwin_amd64 ;;
    *) aviso "Sistema no reconocido: usa AWS CloudShell"; exit 1 ;;
  esac
  BASE="https://releases.hashicorp.com/terraform/$VERSION"
  cd /tmp
  curl -fsSLo "terraform_${VERSION}_${P}.zip" "$BASE/terraform_${VERSION}_${P}.zip"
  curl -fsSL "$BASE/terraform_${VERSION}_SHA256SUMS" | grep "_${P}.zip" > terraform.sha256
  if command -v sha256sum >/dev/null; then sha256sum -c terraform.sha256; else shasum -a 256 -c terraform.sha256; fi
  mkdir -p "$HOME/bin" && unzip -o -q "terraform_${VERSION}_${P}.zip" terraform -d "$HOME/bin"
  rm -f "terraform_${VERSION}_${P}.zip" terraform.sha256
  listo "$(terraform version | head -1) instalado en ~/bin"
fi

titulo "Comprobando la cuenta"
aws sts get-caller-identity --query 'Arn' --output text | sed -E 's/[0-9]{8}([0-9]{4})/••••••••\1/'
echo "Región: $REGION"

titulo "Comprobando que la región permite crear la red"
PERMISO="$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --dry-run 2>&1 || true)"
if grep -q DryRunOperation <<<"$PERMISO"; then
  listo "La región $REGION sirve. Sigue con:  ./2-desplegar.sh"
else
  aviso "Tu cuenta no permite crear redes en $REGION."
  echo "  En la consola, cambia la región (arriba a la derecha), vuelve a abrir CloudShell y repite este paso."
  echo "  En las cuentas nuevas del plan gratuito suele funcionar una sola región; a nosotros nos sirvió Ohio (us-east-2)."
  exit 1
fi
