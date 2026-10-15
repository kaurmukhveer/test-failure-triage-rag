"""Smoke test: is the Gemini key working, and which models can it use?

Run once:  python scripts/check_gemini.py
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

print("Models your key can use:")
for m in client.models.list():
    name = m.name.removeprefix("models/")
    if "flash" in name or "embedding" in name:
        print("  ", name)

embed_model = os.getenv("EMBED_MODEL", "gemini-embedding-001")
gen_model = os.getenv("GEN_MODEL", "gemini-3.1-flash-lite")

result = client.models.embed_content(model=embed_model, contents=["hello"])
print(f"\nEmbedding OK with {embed_model}: vector length {len(result.embeddings[0].values)}")

reply = client.models.generate_content(model=gen_model, contents="Reply with exactly: OK")
print(f"Generation OK with {gen_model}: {reply.text.strip()}")
