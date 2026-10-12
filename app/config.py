import os
from dotenv import load_dotenv

load_dotenv()

# Folders
REPOS_DIR = "data/repos"
CHROMA_DIR = "data/chroma_db"

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Kaun si files padhni hain (values Language enum ke naam se match karti hain)
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "js",
    ".ts": "ts",
    ".java": "java",
    ".cpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".kt": "kotlin",
    ".c": "c",
}

# In folders ko skip karna hai
IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", "tests", "docs", "examples",
}