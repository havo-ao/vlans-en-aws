# ---------- Cómo quedaría la red con IPv6 (doble pila: IPv4 + IPv6) ----------
# Este archivo contiene lo que se AÑADE. Además, en red.tf y computo.tf cambian estos atributos:
#
#   aws_vpc.principal    assign_generated_ipv6_cidr_block = true      (AWS entrega un bloque /56)
#   aws_subnet.*         ipv6_cidr_block = cidrsubnet(aws_vpc.principal.ipv6_cidr_block, 8, N)
#                        assign_ipv6_address_on_creation = true        (cada subred recibe un /64)
#   aws_network_acl.datos  reglas con ipv6_cidr_block para los /64 de la capa de aplicación
#   aws_lb.web           ip_address_type = "dualstack"

# En IPv6 todas las direcciones son públicas y únicas: no existe NAT.
# La capa de aplicación sale por una puerta de enlace "solo de salida".
resource "aws_egress_only_internet_gateway" "salida" {
  vpc_id = aws_vpc.principal.id
  tags   = { Name = "${var.nombre}-solo-salida" }
}

resource "aws_route" "app_ipv6" {
  route_table_id              = aws_route_table.app.id
  destination_ipv6_cidr_block = "::/0"
  egress_only_gateway_id      = aws_egress_only_internet_gateway.salida.id
}

# La capa pública usa la misma puerta de enlace de Internet, con la ruta IPv6 por defecto.
resource "aws_route" "publica_ipv6" {
  route_table_id              = aws_route_table.publica.id
  destination_ipv6_cidr_block = "::/0"
  gateway_id                  = aws_internet_gateway.igw.id
}

# La capa de datos NO recibe ruta ::/0: sigue aislada.

# Las reglas de IPv4 no cubren IPv6: el balanceador necesita su regla para ::/0.
resource "aws_vpc_security_group_ingress_rule" "balanceador_http_ipv6" {
  security_group_id = aws_security_group.balanceador.id
  description       = "HTTP desde Internet por IPv6"
  cidr_ipv6         = "::/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

# Las reglas que nombran a otro Security Group (app y datos) no cambian: valen para IPv4 e IPv6.

# La NACL de datos recibe, dentro del mismo recurso de red.tf, dos reglas más de entrada y dos de
# salida con los rangos /64 de la capa de aplicación (ipv6_cidr_block en lugar de cidr_block).
