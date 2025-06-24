import os
from flask import Flask, session, redirect, url_for, render_template, request, jsonify
from msal import ConfidentialClientApplication
import openai

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET")

# Azure AD / MSAL config
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")
AUTHORITY = (
    f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else None
)
SCOPE = [os.environ.get("AZURE_SCOPE")]

# Azure OpenAI config
OPENAI_ENDPOINT = os.environ.get("OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.environ.get("OPENAI_DEPLOYMENT")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION")
OPENAI_API_TYPE = os.environ.get("OPENAI_API_TYPE", "azure")

if OPENAI_ENDPOINT:
    openai.api_base = OPENAI_ENDPOINT
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
if OPENAI_API_VERSION:
    openai.api_version = OPENAI_API_VERSION
openai.api_type = OPENAI_API_TYPE

@app.route('/')
def index():
    if 'user' not in session:
        # attempt silent login using existing Azure AD session
        return redirect(url_for('login', auto="1"))
    return render_template('index.html', user=session.get('user'))

@app.route('/login')
def login():
    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        return "Missing Azure AD configuration", 500
    prompt = 'none' if request.args.get('auto') == '1' else None
    redirect_uri = url_for('authorized', _external=True)
    cca = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    auth_url = cca.get_authorization_request_url(
        SCOPE, redirect_uri=redirect_uri, prompt=prompt
    )
    return redirect(auth_url)

@app.route('/authorized')
def authorized():
    if 'error' in request.args:
        # user not logged in during silent attempt
        if request.args.get('error') == 'login_required':
            return redirect(url_for('login'))
        return f"Login failure: {request.args.get('error_description')}", 500
    if 'code' not in request.args:
        return redirect(url_for('index'))
    code = request.args['code']
    cca = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    redirect_uri = url_for('authorized', _external=True)
    result = cca.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=redirect_uri)
    if "id_token_claims" in result:
        session['user'] = result['id_token_claims']
        session['access_token'] = result['access_token']
    else:
        return f"Login failure: {result.get('error_description')}", 500
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=" + url_for('index', _external=True)
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'no message'}), 400
    if not (OPENAI_ENDPOINT and OPENAI_DEPLOYMENT):
        return jsonify({'error': 'OpenAI not configured'}), 500
    try:
        response = openai.ChatCompletion.create(
            engine=OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": message}]
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'answer': answer})

if __name__ == '__main__':
    debug = os.environ.get("FLASK_DEBUG", "true").lower() in ["1", "true", "yes"]
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=debug)
