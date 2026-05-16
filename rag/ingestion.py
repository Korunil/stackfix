import json
from langchain_core.documents import Document


def load_stackoverflow_dataset(path):
    docs = []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                try:
                    item = json.loads(line)

                    # Yielding prevents MemoryErrors on massive datasets
                    yield Document(
                        page_content=item["retrieval_text"],
                        metadata={
                            "title": item.get("title", ""),
                            "tags": item.get("tags", []),
                            "score": item.get("score", 0),
                            "question_code": item.get("question_code", []),
                            "answer_code": item.get("answer_code", [])
                        }
                    )
                    
                
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON at line {line_number}")
                
                except KeyError as e:
                    print(f"Missing key {e} at line {line_number}")
    
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "File not found. Please run preload_dataset.py in datasets folder"
            ) from e