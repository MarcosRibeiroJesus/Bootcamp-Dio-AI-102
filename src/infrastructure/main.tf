terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">=3.0"
    }
  }
}

provider "azurerm" {
  features = {}
}

provider "random" {}

resource "random_id" "sa_suffix" {
  byte_length = 3
}

locals {
  sa_name = var.storage_account_name != "" ? var.storage_account_name : substr(lower("antifraudsa"), 0, 10)  # base
  # append random suffix to ensure uniqueness
  storage_account_name = var.storage_account_name != "" ? var.storage_account_name : format("%s%02x", local.sa_name, random_id.sa_suffix.dec)
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "sa" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  kind                     = "StorageV2"
  allow_blob_public_access = false
  min_tls_version          = "TLS1_2"
}

resource "azurerm_storage_container" "containers" {
  for_each = toset(var.containers)

  name                  = each.value
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}
