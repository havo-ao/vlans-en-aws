output "url_aplicacion" {
  description = "Dirección pública de la aplicación (balanceador)."
  value       = "http://${aws_lb.web.dns_name}"
}

output "bd_endpoint" {
  value = aws_db_instance.mysql.address
}

output "ip_salida_nat" {
  value = aws_eip.nat.public_ip
}

output "ids" {
  value = {
    vpc      = aws_vpc.principal.id
    app      = aws_instance.app.id
    pruebas  = aws_instance.pruebas.id
    ip_app   = aws_instance.app.private_ip
    sg_datos = aws_security_group.datos.id
    registro = aws_cloudwatch_log_group.flujo.name
  }
}
