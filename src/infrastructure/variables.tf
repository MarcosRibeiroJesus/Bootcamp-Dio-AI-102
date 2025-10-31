variable "location" {
  description = "Azure region to deploy resources in"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "antifraud-rg"
}

variable "storage_account_name" {
  description = "Optional storage account name. If not set, Terraform will generate one.")
  type        = string
  default     = ""
}

variable "containers" {
  description = "List of blob container names to create"
  type        = list(string)
  default = [
    "bussines-card",
    "contract",
    "credit-card",
    "id-document",
    "invoice",
    "receipt",
  ]
}
