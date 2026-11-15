# ---------- Security Groups encadenados: cada capa solo acepta a la anterior ----------
resource "aws_security_group" "balanceador" {
  name        = "${var.nombre}-sg-balanceador"
  description = "Balanceador: recibe HTTP desde Internet"
  vpc_id      = aws_vpc.principal.id
  tags        = { Name = "${var.nombre}-sg-balanceador" }
}

resource "aws_security_group" "app" {
  name        = "${var.nombre}-sg-app"
  description = "Aplicacion: solo acepta al balanceador en 8080"
  vpc_id      = aws_vpc.principal.id
  tags        = { Name = "${var.nombre}-sg-app" }
}

resource "aws_security_group" "datos" {
  name        = "${var.nombre}-sg-datos"
  description = "Base de datos: solo acepta a la aplicacion en 3306"
  vpc_id      = aws_vpc.principal.id
  tags        = { Name = "${var.nombre}-sg-datos" }
}

resource "aws_security_group" "pruebas" {
  name        = "${var.nombre}-sg-pruebas"
  description = "Equipo de pruebas en la subred publica: sin entradas"
  vpc_id      = aws_vpc.principal.id
  tags        = { Name = "${var.nombre}-sg-pruebas" }
}

resource "aws_vpc_security_group_ingress_rule" "balanceador_http" {
  security_group_id = aws_security_group.balanceador.id
  description       = "HTTP desde Internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "balanceador_a_app" {
  security_group_id            = aws_security_group.balanceador.id
  description                  = "Solo hacia la aplicacion"
  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 8080
  to_port                      = 8080
}

resource "aws_vpc_security_group_ingress_rule" "app_desde_balanceador" {
  security_group_id            = aws_security_group.app.id
  description                  = "Solo desde el balanceador"
  referenced_security_group_id = aws_security_group.balanceador.id
  ip_protocol                  = "tcp"
  from_port                    = 8080
  to_port                      = 8080
}

resource "aws_vpc_security_group_egress_rule" "app_salida" {
  security_group_id = aws_security_group.app.id
  description       = "Salida (base de datos y actualizaciones por el NAT)"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "datos_desde_app" {
  security_group_id            = aws_security_group.datos.id
  description                  = "MySQL solo desde la aplicacion"
  referenced_security_group_id = aws_security_group.app.id
  ip_protocol                  = "tcp"
  from_port                    = 3306
  to_port                      = 3306
}

resource "aws_vpc_security_group_egress_rule" "pruebas_salida" {
  security_group_id = aws_security_group.pruebas.id
  description       = "Salida libre para lanzar las pruebas"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# ---------- Permiso para administrar los servidores sin abrir SSH (Systems Manager) ----------
resource "aws_iam_role" "servidores" {
  name = "${var.nombre}-servidores"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "servidores_ssm" {
  role       = aws_iam_role.servidores.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "servidores" {
  name = "${var.nombre}-servidores"
  role = aws_iam_role.servidores.name
}
