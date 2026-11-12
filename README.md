# VLANs en AWS — Proyecto final de Redes de Datos II

**Presentación en línea:** https://havo-ao.github.io/vlans-en-aws/

Juan José Ascuntar · Andrés Felipe Cañón — Universidad El Bosque, Facultad de Ingeniería.

Red de tres capas (pública, aplicación y datos) en una VPC de AWS, creada con Terraform, con una aplicación mínima en Docker y pruebas que demuestran el aislamiento.

| Carpeta | Contenido |
|---|---|
| `presentacion/` | `VLANs_en_AWS.html` (abrir en el navegador; flechas para avanzar, `F` pantalla completa) y `VLANs_en_AWS.pdf` |
| `infra/` | Terraform: `red.tf`, `seguridad.tf`, `datos.tf`, `computo.tf` |
| `app/` | API de reservas (Node.js + MySQL) y su `Dockerfile` |
| `pruebas/` | `pruebas.py` y `resultados.json` |
| `capturas/` | Evidencias de la terminal y de las pruebas |
| `docs/` | Copia de la presentación que publica GitHub Pages |

## Desplegar
```bash
cd infra
terraform init
terraform apply
```
Requiere la CLI de AWS configurada (`aws configure`) en la región habilitada para la cuenta (aquí `us-east-2`). Tarda unos 7 minutos y crea 46 recursos.

## Probar
```bash
cd pruebas && python3 pruebas.py
```

## Destruir (para no gastar créditos)
```bash
cd infra && terraform destroy
```
El NAT, el balanceador y la base de datos consumen créditos por hora mientras existan.
