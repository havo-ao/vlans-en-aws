data "aws_ssm_parameter" "ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

# ---------- Capa de aplicación: servidor privado que construye y ejecuta el contenedor ----------
resource "aws_instance" "app" {
  ami                         = data.aws_ssm_parameter.ami.value
  instance_type               = "t4g.micro"
  subnet_id                   = aws_subnet.app[0].id
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.servidores.name
  user_data_replace_on_change = true
  user_data_base64 = base64gzip(templatefile("${path.module}/arranque_app.sh.tftpl", {
    archivos = {
      "package.json"      = filebase64("${path.module}/../app/package.json")
      "Dockerfile"        = filebase64("${path.module}/../app/Dockerfile")
      "server.js"         = filebase64("${path.module}/../app/server.js")
      "public/index.html" = filebase64("${path.module}/../app/public/index.html")
    }
    bd_host = aws_db_instance.mysql.address
    bd_user = aws_db_instance.mysql.username
    bd_pass = random_password.bd.result
    bd_name = aws_db_instance.mysql.db_name
  }))
  metadata_options {
    http_tokens = "required"
  }
  tags       = { Name = "${var.nombre}-app" }
  depends_on = [aws_route_table_association.app, aws_nat_gateway.nat]
}

# ---------- Equipo de pruebas en la subred pública: desde aquí se intenta llegar a las capas privadas ----------
resource "aws_instance" "pruebas" {
  ami                    = data.aws_ssm_parameter.ami.value
  instance_type          = "t4g.micro"
  subnet_id              = aws_subnet.publica[0].id
  vpc_security_group_ids = [aws_security_group.pruebas.id]
  iam_instance_profile   = aws_iam_instance_profile.servidores.name
  metadata_options {
    http_tokens = "required"
  }
  tags       = { Name = "${var.nombre}-pruebas" }
  depends_on = [aws_route_table_association.publica]
}

# ---------- Capa pública: balanceador de carga ----------
resource "aws_lb" "web" {
  name               = "${var.nombre}-balanceador"
  load_balancer_type = "application"
  subnets            = aws_subnet.publica[*].id
  security_groups    = [aws_security_group.balanceador.id]
}

resource "aws_lb_target_group" "app" {
  name     = "${var.nombre}-app"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.principal.id
  health_check {
    path                = "/api/health"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_target_group_attachment" "app" {
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app.id
  port             = 8080
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
