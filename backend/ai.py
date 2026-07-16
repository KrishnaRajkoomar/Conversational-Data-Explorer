import os
import certifi
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

_api_key = os.getenv("GEMINI_API_KEY")
_client = None


def get_client():
    global _client
    if _client is None:
        if not _api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Create a .env file with your key.")
        from google import genai
        _client = genai.Client(api_key=_api_key)
    return _client


def generate(prompt: str) -> str:
    client = get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()
