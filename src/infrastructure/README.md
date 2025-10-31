# Infrastructure (Terraform)

This folder contains a minimal Terraform example that provisions the Azure resources used by the anti-fraud service.

What it creates
- Resource Group
- Storage Account (StorageV2)
- Blob containers for the service (defaults: bussines-card, contract, credit-card, id-document, invoice, receipt)

Usage

1. Configure Azure credentials (e.g., using `az login` or a service principal). When running in GitHub Actions, provide a service principal JSON in `secrets.AZURE_CREDENTIALS`.

2. Initialize and plan locally

```powershell
cd infrastructure
terraform init
terraform plan -var "resource_group_name=my-rg" -var "location=eastus"
```

3. Apply

```powershell
terraform apply -var "resource_group_name=my-rg" -var "location=eastus" -auto-approve
```

Notes
- The storage account name must be globally unique; you may pass `-var "storage_account_name=youruniquename"` to use a fixed name.
- This is a starter example. For production use you should:
  - Configure a remote state backend (e.g., azurerm backend) and ensure the service principal has access
  - Harden storage account network rules and disable public access if appropriate
  - Add role assignments if you want to grant the GH Actions SP access to a specific resource group or storage account
