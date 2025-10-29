
[OpenAI Translator.webm](https://github.com/user-attachments/assets/ea47bec4-5d9e-490c-bfa1-3afd02ea8056)


<img width="3804" height="1831" alt="image" src="https://github.com/user-attachments/assets/eb3ec385-d063-484f-89f6-26ff03dc657d" />

## Python translator app (Flask) — run & deploy

This folder contains a small Flask app that:

- extracts text from URLs, PDF and DOCX files
- translates text using your Azure OpenAI (Chat) deployment


## Quick start (local)

Create a virtualenv and install dependencies:
```bash
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```
Copy ```.env.example``` to ```.env``` and fill the values (especially ```AZURE_OPENAI_KEY```, ```AZURE_OPENAI_ENDPOINT```, and ```AZURE_OPENAI_DEPLOYMENT```).

Run the app locally:

$env:FLASK_ENV="development"; python src/app.py
Endpoints

```
POST /translate/url

JSON body: {"url": "https://example.com/article", "lang": "português"}
Response: {"translation": "..."}
```
```
POST /translate/upload

Form-data: file (pdf or docx), lang (optional)
Response: {"translation": "..."}
```


## Production deployment options (free / low-cost)

### Azure Functions (Consumption Plan)

Good low-cost option for HTTP-triggered workloads. Cold starts possible, but you only pay for executions. Works well if translation requests are occasional.
Convert this Flask app into an Azure Function by using an HTTP trigger and calling the same helper modules (extractors.py and translate_service.py). Alternatively, containerize the Flask app and deploy to Functions custom container.

### Azure App Service (Free / Shared)

App Service has a free tier for basic testing in some subscriptions. If available, you can deploy the Flask app using a simple Git deployment or using Docker.
For consistent performance, use a Linux App Service plan (B1 or similar) if you can accept a small cost.
Recommendation

Start with Azure Functions (Consumption) for the lowest cost. If you need persistent low-latency service, move to App Service or a small container.


## Security and production notes

Never commit secrets to the repository. Use Azure App Settings or Functions Application Settings to set ```AZURE_OPENAI_KEY```, ```AZURE_OPENAI_ENDPOINT```, and ```AZURE_OPENAI_DEPLOYMENT```.
Consider storing the OpenAI key in Azure Key Vault and using a Managed Identity to retrieve it.
Add rate-limiting and request size limits to prevent abuse.
Add authentication (API key or OAuth) before enabling public access.


## Next steps you can implement:

Provide an Azure Functions HTTP trigger version (function app) that reuses the same modules.
Add a Dockerfile and GitHub Actions workflow to build and deploy to Azure Web App for Containers.
Add response as downloadable translated DOCX.
Create the deployment artifacts and instructions (Azure Functions or App Service + GitHub Actions).
