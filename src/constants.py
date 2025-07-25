import os


OVERALL_MODEL  = os.getenv("OVERALL_MODEL", "openAI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY" , "sk-proj-...")
OPENAI_VERSION = os.getenv("OPENAI_VERSION","gpt-4o-2024-08-06")


print(OPENAI_API_KEY)