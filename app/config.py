import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("LLM_API_KEY"))
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leave.db")
POLICY_VECTOR_DIR = os.getenv("POLICY_VECTOR_DIR", "./data/chroma")
