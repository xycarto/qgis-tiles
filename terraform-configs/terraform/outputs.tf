output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.qgis_tiles.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.qgis_tiles.public_ip
}

output "instance_name" {
  description = "Name of Instance"
  value       = aws_instance.qgis_tiles[*].tags["Name"]
}