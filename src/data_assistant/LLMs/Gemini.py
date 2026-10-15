import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_gemini_llm(model: str = "gemini-3.8-flash") -> ChatGoogleGenerativeAI:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is missing. Please set it in your .env file.")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.0,
    )

class _LazyGeminiLLM:
    """Lazily initializes ChatGoogleGenerativeAI on first access."""
    def __init__(self, model: str = "gemini-3.8-flash"):
        self.model = model
        self._llm = None

    def _get_instance(self):
        if self._llm is None:
            self._llm = get_gemini_llm(self.model)
        return self._llm

    def invoke(self, *args, **kwargs):
        return self._get_instance().invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        return await self._get_instance().ainvoke(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

llm_gemini = _LazyGeminiLLM()