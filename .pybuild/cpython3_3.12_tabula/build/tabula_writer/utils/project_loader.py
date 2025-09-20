import os

def load_project(base_path):
    """Load project with documents instead of chapters, scanning recursively."""
    documents_path = os.path.join(base_path, "documents")
    notes_path = os.path.join(base_path, "notes")

    os.makedirs(documents_path, exist_ok=True)
    os.makedirs(notes_path, exist_ok=True)

    documents = []
    # Use os.walk to find all .md files in all subdirectories
    for root, _, files in os.walk(documents_path):
        for file in files:
            if file.endswith(".md"):
                documents.append(os.path.join(root, file))
    
    documents.sort()

    return base_path, documents, notes_path
