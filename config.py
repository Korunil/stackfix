import ssl
import os

# The Offline mode
LOCAL_MODE = False
if LOCAL_MODE:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Verify SSL
VERIFY_SSL = True
if not VERIFY_SSL:
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context



CACHE_DIR = "./model_cache"

JSON_PATH = "./datasets/processed/stackoverflow.jsonl"



MAX_NEW_TOKENS = 350


MODEL_MAP = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    "mistral2": "mistralai/Mistral-7B-Instruct-v0.3",
    "llama": "meta-llama/Meta-Llama-3-8B-Instruct"
}

#EMBEDDING
EMBEDDING_MAP = {
    "fast": "sentence-transformers/all-MiniLM-L6-v2",
    "balanced": "BAAI/bge-base-en-v1.5",
    "better": "BAAI/bge-large-en-v1.5",
    "strong": "intfloat/e5-large-v2",
}
DEVICE_EMBEDDINGS = "cpu"
NORMALIZE_EMBEDDINGS = True

#RERANKER
CROSS_ENCODER = "BAAI/bge-reranker-base"
CROSS_ENCODER_LIGHT = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEVICE_RERANKER = "cpu"


K = 5
TOP_K = 3
FETCH_K = 20
BATCH_SIZE=32

BM25_WEIGHT = 0.4
VECTOR_WEIGHT = 0.6

LIVE_SEARCH_ENABLED = False
GITHUB_API = "https://api.github.com/search/issues"

#PRESETS PER TASK
GENERATION_CONFIGS = {

    "debug": {
        "repetition_penalty": 1.12,
        "temperature": 0.2,
        "top_p": 0.9,
    },

    "fallback": {
        "repetition_penalty": 1.1,
        "temperature": 0.35,
        "top_p": 0.92,
    }
}

MODERN_KEYWORDS = [

    # LangChain ecosystem
    "langchain",
    "langchain_core",
    "langchain_community",
    "langchain_huggingface",
    "langserve",

    # Llama ecosystem
    "llamaindex",
    "llama-index",

    # HF ecosystem
    "transformers",
    "peft",
    "accelerate",
    "bitsandbytes",

    # frontend
    "nextjs",
    "next.js",
    "vite",

    # backend
    "fastapi",

    # AI tooling
    "ollama",
    "vllm",
    "litellm",
    "autogen",

    # vector db
    "chromadb",
    "qdrant",
    "weaviate"
]

LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "go",
    "rust",
    "php",
    "ruby"
]

FRAMEWORKS = [
    "react",
    "nextjs",
    "next.js",
    "django",
    "flask",
    "fastapi",
    "spring",
    "tensorflow",
    "pytorch",
    "numpy",
    "pandas"
]


ERROR_PATTERNS = [
    r"Traceback \(most recent call last\):",
    r"\w+Error",
    r"\w+Exception",
    r"ModuleNotFoundError",
    r"TypeError",
    r"ValueError",
    r"SyntaxError",
    r"RuntimeError",
    r"ImportError",
    r"KeyError",
    r"AttributeError",
    r"NameError",
    r"IndexError",
    r"Segmentation fault",
    r"NullPointerException",
    r"CompilerError",
]

ERROR_SYNONYMS = {
    "ModuleNotFoundError": [
        "missing package",
        "import issue",
        "dependency error"
    ],

    "TypeError": [
        "invalid type",
        "wrong argument type"
    ],

    "KeyError": [
        "missing dictionary key",
        "dict lookup failure"
    ]
}

PACKAGE_HINTS = {
    "langchain_huggingface": [
        "langchain-huggingface",
        "huggingface embeddings",
        "langchain package split",
        "langchain 0.2 migration"
    ]
}

MODERN_PACKAGES = [
    "langchain_huggingface",
    "langchain_openai",
    "langchain_core",
    "langchain_community",
    "llama_index",
    "transformers"
]

TRUSTED_DOMAINS = [
    "github.com",
    "stackoverflow.com",
    "python.langchain.com",
    "docs.python.org",
    "pytorch.org",
    "tensorflow.org",
    "fastapi.tiangolo.com",
    "react.dev",
    "nextjs.org"
]
