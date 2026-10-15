import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_groq_llm(model: str = "qwen/qwen3.8-27b") -> ChatGroq:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")
    return ChatGroq(
        model=model,
        api_key=groq_api_key,
        temperature=0.0,
    )

class _LazyGroqLLM:
    """Lazily initializes ChatGroq on first access."""
    def __init__(self, model: str = "qwen/qwen3.8-27b"):
        self.model = model
        self._llm = None

    def _get_instance(self):
        if self._llm is None:
            self._llm = get_groq_llm(self.model)
        return self._llm

    def invoke(self, *args, **kwargs):
        return self._get_instance().invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        return await self._get_instance().ainvoke(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

llm_groq = _LazyGroqLLM()