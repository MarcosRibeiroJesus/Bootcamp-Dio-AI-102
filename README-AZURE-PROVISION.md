# Provision Azure resources (GitHub Actions)

This document explains how to run the GitHub Action that provisions the Azure resources required for the article translation project (resource group + Azure OpenAI / Cognitive Services account), and how to provide the necessary GitHub secrets.

Important notes and assumptions
- The workflow will create a resource group and a Cognitive Services account with kind `OpenAI` (SKU: S0 by default).
- The action uses a Service Principal (CI/CD) to authenticate. Do NOT store client secrets in repo files; use GitHub repository secrets.
- Azure OpenAI often requires subscription registration/approval; some subscriptions may not be eligible for programmatic creation. If account creation fails, you may need to request access in the Azure portal or use Azure OpenAI Studio to create a deployment manually.

Secrets required
- `AZURE_CREDENTIALS` — a Service Principal JSON produced by `az ad sp create-for-rbac --sdk-auth` (see steps below).

Create a Service Principal and set the GitHub secret
1. Login to Azure CLI (PowerShell):

```powershell
az login
```

2. Create a service principal with the minimal scope you need. Example (replace `<subscriptionId>`):

```powershell
az ad sp create-for-rbac --name "github-action-sp" --role "Contributor" --scopes /subscriptions/<subscriptionId>
```

This command returns a JSON blob suitable for the `AZURE_CREDENTIALS` repository secret (the value you pass to the `azure/login` action's `creds` input). Copy the JSON exactly and add it as a GitHub repository secret named `AZURE_CREDENTIALS`.

Running the workflow
1. Open the repository on GitHub, go to the Actions tab, select "Provision Azure resources for Translator" and click "Run workflow".
2. Fill the inputs (location, resource_group, account_name, sku) and dispatch.
3. When the job completes successfully, the workflow uploads an artifact named `azure-credentials` containing `azure_keys.env` with two lines:

```
AZURE_OPENAI_KEY=<key>
AZURE_ENDPOINT=<endpoint>
```

Security and best-practices notes
- Prefer scoping the Service Principal to only the subscription or resource group the workflow will manage (least privilege). Replace `Contributor` with a more-restrictive role if appropriate.
- Consider storing keys in Azure Key Vault and wiring the project to fetch secrets at runtime rather than baking keys into files.
- For production CI pipelines prefer Managed Identity where supported.

Model deployment note
- Creating a Cognitive Services account only provisions the service. Deploying an OpenAI model (for example GPT-4 mini) is typically done in the Azure OpenAI Studio or via the service management APIs. Many tenants must be approved to use specific OpenAI models. If you need help automating the model deployment, I can add optional REST/CLI snippets, but some tenant approvals block programmatic deployment.

If you want, I can also:
- Add an ARM/Bicep template variant instead of the CLI commands.
- Add a pipeline step that attempts a programmatic deployment of a specific model (if your subscription supports it).

Troubleshooting: role assignment / MissingSubscription errors
--------------------------------------------------------

If you see an error like:

	role assignment creation failed ... (MissingSubscription) The request did not have a subscription or a valid tenant level resource provider.

This usually means the CLI request tried to create a role assignment at a subscription scope but either:

- your CLI isn't set to the correct subscription, or
- you're logged into a tenant that doesn't contain that subscription, or
- your account doesn't have permission to create role assignments at the requested scope.

Quick checks and fixes (PowerShell / Azure CLI)

1) Verify which subscription(s) you have access to:

```powershell
az account list --output table
```

2) Ensure the CLI is set to the subscription you want to use (replace `<subscriptionId>`):

```powershell
az account set --subscription <subscriptionId>
az account show --query "{name:name,id:id,tenantId:tenantId}" -o table
```

3) If the subscription is in a different tenant, log in to the correct tenant (replace `<tenantId>`):

```powershell
az login --tenant <tenantId>
```

4) If you don't have permission to create role assignments at the subscription root, use a narrower scope (resource group) or ask the subscription owner to run the SP creation/role assignment. Example (resource-group scope):

```powershell
az ad sp create-for-rbac --name "github-action-sp" --role "Contributor" --scopes /subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName> --sdk-auth
```

5) If role assignment fails during `az ad sp create-for-rbac` and you want to create the service principal without assignments (then ask the owner/admin to grant permissions), use `--skip-assignment`:

```powershell
az ad sp create-for-rbac --name "github-action-sp" --skip-assignment --sdk-auth

# Then have an owner run (example):
az role assignment create --assignee <appId-or-objectId> --role Contributor --scope /subscriptions/<subscriptionId>
```

6) Common causes and guidance
- If you're a guest user in the subscription's tenant you may not have permission to create role assignments — ask the tenant/subscription owner to create the SP or grant you a role that can.
- If the subscription ID in the `--scopes` argument is mistyped or belongs to another directory, role assignment will fail.
- Some organizational policies restrict programmatic creation of certain resource types; try creating the SP and the Cognitive Services resource via the portal to confirm policies.
