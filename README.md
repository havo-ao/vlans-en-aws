# VLANs en AWS — Proyecto final de Redes de Datos II

Cómo se logra en AWS lo que en una red tradicional hacen las VLANs: una red de tres capas (pública, aplicación y datos) en una VPC, creada con Terraform, con una aplicación en Docker y pruebas que demuestran el aislamiento.

Juan José Ascuntar · Andrés Felipe Cañón — Universidad El Bosque, Facultad de Ingeniería.

| | |
|---|---|
| **Presentación en línea** | https://havo-ao.github.io/vlans-en-aws/ |
| **Manual paso a paso** | [manual/MANUAL.md](manual/MANUAL.md) · [PDF](manual/Manual_VLANs_en_AWS.pdf) |

## Hazlo tú mismo en cuatro comandos

No hay que instalar nada: se hace desde el navegador, en AWS CloudShell. El [manual](manual/MANUAL.md) explica cada paso desde cero, incluida la creación de la cuenta.

```bash
git clone https://github.com/havo-ao/vlans-en-aws.git && cd vlans-en-aws
./1-preparar.sh     # instala Terraform y revisa la cuenta y la región
./2-desplegar.sh    # crea la red: 46 recursos, unos 7 minutos
./3-probar.sh       # siete pruebas de aislamiento
./4-destruir.sh     # borra todo para no gastar créditos
```

## Qué hay en el repositorio

| Carpeta | Contenido |
|---|---|
| `manual/` | El manual para principiantes, con sus imágenes |
| `infra/` | La red en Terraform: `red.tf`, `seguridad.tf`, `datos.tf`, `computo.tf` |
| `app/` | API de reservas (Node.js + MySQL) y su `Dockerfile` |
| `pruebas/` | `pruebas.py` y los resultados de nuestra ejecución |
| `ejemplos/ipv6/` | La misma red con IPv6 (validada con `terraform plan`, no desplegada) |
| `presentacion/` | La presentación en HTML y PDF, y sus fuentes |
| `docs/` | Copia de la presentación que publica GitHub Pages |
| `capturas/` | Evidencias de la terminal y de las pruebas |

## La red

```
Internet ──80──▶ Balanceador ──8080──▶ Aplicación ──3306──▶ MySQL
                 capa pública          capa privada         capa de datos
                 10.0.1-2.0/24         10.0.11-12.0/24      10.0.21-22.0/24
                 sale a Internet       sale solo por NAT    sin salida
```

Tres barreras independientes separan las capas: las tablas de ruteo, los Security Groups encadenados (cada capa solo acepta a la anterior) y una NACL en la subred de datos.

## Costo

La red consume créditos mientras existe (NAT, balanceador, base de datos y servidores). En nuestra cuenta fueron unos 20 USD de crédito en tres días. Con el plan gratuito de AWS no hay cobro en dinero, pero conviene ejecutar `./4-destruir.sh` al terminar.
