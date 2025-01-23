from pathlib import Path
import json

def load_json(file_path: Path) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

def save_json(data: dict, file_path: Path) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
