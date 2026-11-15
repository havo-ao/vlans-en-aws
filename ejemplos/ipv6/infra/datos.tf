# ---------- Capa de datos: MySQL administrado, sin IP pública ----------
resource "random_password" "bd" {
  length  = 24
  special = false
}

resource "aws_db_subnet_group" "datos" {
  name       = "${var.nombre}-datos"
  subnet_ids = aws_subnet.datos[*].id
}

resource "aws_db_instance" "mysql" {
  identifier              = "${var.nombre}-mysql"
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t4g.micro"
  allocated_storage       = 20
  storage_type            = "gp2"
  db_name                 = "reservas"
  username                = "reservas_app"
  password                = random_password.bd.result
  db_subnet_group_name    = aws_db_subnet_group.datos.name
  vpc_security_group_ids  = [aws_security_group.datos.id]
  publicly_accessible     = false
  multi_az                = false
  backup_retention_period = 0
  skip_final_snapshot     = true
  apply_immediately       = true
}
