variable "region" {
  description = "Región de AWS. Usa la que tu cuenta tenga habilitada (se ve en la URL de la consola)."
  type        = string
  default     = "us-east-2"
}

variable "nombre" {
  description = "Prefijo para nombrar los recursos."
  type        = string
  default     = "vlans"
}
