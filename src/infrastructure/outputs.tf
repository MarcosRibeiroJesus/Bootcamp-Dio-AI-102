output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  value = azurerm_storage_account.sa.name
}

output "blob_primary_endpoint" {
  value = azurerm_storage_account.sa.primary_blob_endpoint
}

output "container_names" {
  value = [for c in azurerm_storage_container.containers : c.name]
}
