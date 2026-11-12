# ---------- La VPC: el equivalente a toda la red del campus ----------
resource "aws_vpc" "principal" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${var.nombre}-vpc" }
}

data "aws_availability_zones" "disponibles" {
  state = "available"
}

locals {
  zonas = slice(data.aws_availability_zones.disponibles.names, 0, 2)
}

# ---------- Subredes: el equivalente a las VLANs (una por capa y por zona) ----------
resource "aws_subnet" "publica" {
  count                   = 2
  vpc_id                  = aws_vpc.principal.id
  cidr_block              = "10.0.${1 + count.index}.0/24"
  availability_zone       = local.zonas[count.index]
  map_public_ip_on_launch = true
  tags                    = { Name = "${var.nombre}-publica-${count.index + 1}", Capa = "publica" }
}

resource "aws_subnet" "app" {
  count             = 2
  vpc_id            = aws_vpc.principal.id
  cidr_block        = "10.0.${11 + count.index}.0/24"
  availability_zone = local.zonas[count.index]
  tags              = { Name = "${var.nombre}-app-${count.index + 1}", Capa = "aplicacion" }
}

resource "aws_subnet" "datos" {
  count             = 2
  vpc_id            = aws_vpc.principal.id
  cidr_block        = "10.0.${21 + count.index}.0/24"
  availability_zone = local.zonas[count.index]
  tags              = { Name = "${var.nombre}-datos-${count.index + 1}", Capa = "datos" }
}

# ---------- Salida a Internet ----------
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.principal.id
  tags   = { Name = "${var.nombre}-igw" }
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = { Name = "${var.nombre}-nat-ip" }
}

# El NAT deja que la capa de aplicación salga a Internet (actualizaciones) sin ser alcanzable desde afuera.
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.publica[0].id
  tags          = { Name = "${var.nombre}-nat" }
  depends_on    = [aws_internet_gateway.igw]
}

# ---------- Tablas de ruteo: el equivalente al enrutamiento entre VLANs ----------
resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.principal.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.nombre}-rt-publica" }
}

resource "aws_route_table" "app" {
  vpc_id = aws_vpc.principal.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = { Name = "${var.nombre}-rt-app" }
}

# La tabla de datos no tiene ruta a Internet: solo conoce la red interna (ruta local implícita).
resource "aws_route_table" "datos" {
  vpc_id = aws_vpc.principal.id
  tags   = { Name = "${var.nombre}-rt-datos" }
}

resource "aws_route_table_association" "publica" {
  count          = 2
  subnet_id      = aws_subnet.publica[count.index].id
  route_table_id = aws_route_table.publica.id
}

resource "aws_route_table_association" "app" {
  count          = 2
  subnet_id      = aws_subnet.app[count.index].id
  route_table_id = aws_route_table.app.id
}

resource "aws_route_table_association" "datos" {
  count          = 2
  subnet_id      = aws_subnet.datos[count.index].id
  route_table_id = aws_route_table.datos.id
}

# ---------- NACL de la capa de datos: el equivalente a la ACL del router (sin estado) ----------
resource "aws_network_acl" "datos" {
  vpc_id     = aws_vpc.principal.id
  subnet_ids = aws_subnet.datos[*].id

  dynamic "ingress" {
    for_each = aws_subnet.app
    content {
      rule_no    = 100 + ingress.key * 10
      protocol   = "tcp"
      action     = "allow"
      cidr_block = ingress.value.cidr_block
      from_port  = 3306
      to_port    = 3306
    }
  }

  # Al no tener estado, la respuesta necesita su propia regla de salida (puertos efímeros).
  dynamic "egress" {
    for_each = aws_subnet.app
    content {
      rule_no    = 100 + egress.key * 10
      protocol   = "tcp"
      action     = "allow"
      cidr_block = egress.value.cidr_block
      from_port  = 1024
      to_port    = 65535
    }
  }

  tags = { Name = "${var.nombre}-nacl-datos" }
}

# ---------- Registros de tráfico (flow logs): la evidencia de lo aceptado y lo rechazado ----------
resource "aws_cloudwatch_log_group" "flujo" {
  name              = "/vpc/${var.nombre}-flujo"
  retention_in_days = 7
}

resource "aws_iam_role" "flujo" {
  name = "${var.nombre}-flow-logs"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "vpc-flow-logs.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "flujo" {
  name = "escribir-registros"
  role = aws_iam_role.flujo.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogGroups", "logs:DescribeLogStreams"]
      Resource = "*"
    }]
  })
}

resource "aws_flow_log" "vpc" {
  vpc_id                   = aws_vpc.principal.id
  traffic_type             = "ALL"
  log_destination          = aws_cloudwatch_log_group.flujo.arn
  iam_role_arn             = aws_iam_role.flujo.arn
  max_aggregation_interval = 60
  tags                     = { Name = "${var.nombre}-flow-log" }
}
