# La misma red con IPv6 (doble pila)

Variante de `infra/` en la que la VPC y las subredes tienen, además de IPv4, direcciones IPv6.

**Estado:** validada con `terraform validate` y `terraform plan` (50 recursos). No se desplegó.

## Qué cambia frente a `infra/`

| Archivo | Cambio |
|---|---|
| `red.tf` | La VPC pide un bloque IPv6 `/56` a AWS; cada subred recibe un `/64`; la NACL de datos suma las reglas para los rangos IPv6 de la capa de aplicación |
| `computo.tf` | El balanceador pasa a modo doble pila (`dualstack`) |
| `ipv6.tf` (nuevo) | Puerta de enlace solo de salida, rutas `::/0` y la regla IPv6 del balanceador |

## La idea central

En IPv6 todas las direcciones son públicas y únicas, así que no existe NAT. Para que la capa de
aplicación pueda salir a Internet sin que nadie pueda iniciar una conexión hacia ella se usa una
**puerta de enlace solo de salida** (*egress-only internet gateway*). La capa de datos no recibe
ninguna ruta `::/0` y sigue aislada. El NAT se conserva únicamente para el tráfico IPv4.

## Probarlo

```bash
cd ejemplos/ipv6/infra
terraform init
terraform plan
```
