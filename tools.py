import os

# Define the folder structure
structure = {
    "ui-backend": {
        "templates": ["index.html", "result.html"],
        "static": ["style.css", "script.js"],
        "files": ["app.py", "requirements.txt", "Dockerfile"]
    },
    "ai-backend": {
        "files": ["app.py", "detector.py", "utils.py", "requirements.txt", "Dockerfile"]
    },
    "outputs": {},
    "test_images": {},
    "files": ["docker-compose.yml", "README.md", "run.sh"]
    
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        dir_path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(dir_path, exist_ok=True)
            files = content.get("files", [])
            for f in files:
                open(os.path.join(dir_path, f), "a").close()
            for subname, subcontent in content.items():
                if subname not in ["files"]:
                    create_structure(dir_path, {subname: subcontent})
        else:
            os.makedirs(base_path, exist_ok=True)
            for f in content:
                open(os.path.join(base_path, f), "a").close()

if __name__ == "__main__":
    create_structure(".", structure)

