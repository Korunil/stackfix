import os
from langchain_huggingface import HuggingFaceEmbeddings
from config import DEVICE_EMBEDDINGS, NORMALIZE_EMBEDDINGS, CACHE_DIR
from cache_store import _EMBED_CACHE

def get_embeddings(embedding_map, embed_choice, device_override=None):
    
    embedding_name = embedding_map.get(embed_choice, embedding_map["balanced"])
    
    # Use the override if provided, otherwise fallback to config.py
    actual_device = device_override if device_override else DEVICE_EMBEDDINGS
    
    # Check if the environment variable is set for offline mode
    # This allows users to toggle 'local_files_only' without changing code
    is_offline = os.getenv("HF_HUB_OFFLINE", "0") == "1"
    
    # Update cache key to prevent CPU/GPU cache mixing
    cache_key = f"{embedding_name}_{actual_device}"
    
    if cache_key in _EMBED_CACHE:
        return _EMBED_CACHE[cache_key]

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_name,
        cache_folder=CACHE_DIR,
        model_kwargs={"device": actual_device,
            "local_files_only": is_offline
        },
        encode_kwargs={
            "normalize_embeddings" : NORMALIZE_EMBEDDINGS
        },
    )
     
    _EMBED_CACHE[cache_key] = embeddings
    return embeddings