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
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")

# File extensions to process (values must match names in the Language enum).
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

# Directories to skip during repository scanning.
IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", "tests", "docs", "examples",
}
