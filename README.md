# Azure OpenAI Chatbot

This project provides a simple ChatGPT‑like web interface that authenticates users with Azure AD (SSO) and forwards prompts to a model hosted on Azure OpenAI. Chat history is stored in the browser session for the signed‑in user only.

## Features

* **Azure AD SSO** using the [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python) library.
* **Connect to Azure OpenAI** by specifying your endpoint and deployment name.
* **Chat history stored locally** via `sessionStorage` in the browser.

* **Automatic login** when a valid Azure AD session already exists.


## Setup

1. Create an Azure AD application registration and configure redirect URIs.
2. Deploy a model using Azure OpenAI and note the endpoint and deployment name.
3. Set the following environment variables before starting the app:

```
FLASK_SECRET=replace-with-random-string
AZURE_CLIENT_ID=<application-client-id>
AZURE_CLIENT_SECRET=<application-client-secret>
AZURE_TENANT_ID=<tenant-id>
AZURE_SCOPE=<scope-for-token>  # usually "api://<app-id>/.default"
OPENAI_ENDPOINT=<https://your-openai-resource.openai.azure.com/>
OPENAI_DEPLOYMENT=<name-of-your-deployment>
OPENAI_API_KEY=<api-key-for-openai-resource>
OPENAI_API_VERSION=<api-version>
# Optional: override defaults
OPENAI_API_TYPE=azure
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=true
```

Install dependencies and run the server:

```bash
pip install -r requirements.txt
python app.py
```

Navigate to `http://localhost:5000` and sign in with your Azure AD credentials.


If you already have an active Azure AD session in the browser, the app will
attempt a silent login so opening a new tab won't prompt you again.


## Notes

This is a basic sample intended for demonstration purposes. Production deployments should use HTTPS, proper session storage, CSRF protection and improved error handling.
