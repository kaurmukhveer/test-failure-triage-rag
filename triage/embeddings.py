"""Turn text into vectors ("GPS coordinates for meaning").

Texts with similar meaning get vectors that point in similar directions,
even when they use different words ("Killed, exit code 137" vs "out of memory").
"""

import os

import numpy as np
from google import genai
from google.genai import types


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Scale every vector to length 1.

    After this, the dot product of two vectors IS their cosine similarity
    (1.0 = same direction/meaning, 0 = unrelated).
    """
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)


class GeminiEmbedder:
    """Calls the Gemini embedding API.

    Documents and queries use different task types: Google trains the model to
    place a question close to the passage that answers it.
    """

    def __init__(self, model: str | None = None, dimensions: int = 768):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = model or os.getenv("EMBED_MODEL", "gemini-embedding-001")
        self.dimensions = dimensions

    def _embed(self, texts: list[str], task_type: str) -> np.ndarray:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.dimensions,
            ),
        )
        vectors = np.array([e.values for e in result.embeddings], dtype=np.float32)
        return normalize(vectors)  # required for gemini-embedding-001 below 3072 dims

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed([text], "RETRIEVAL_QUERY")[0]
