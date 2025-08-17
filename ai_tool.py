#!/usr/bin/env python3
"""
collect_code_files.py

Collect specified source files into a single text file (all_code_data.txt).
If a file is missing, the script logs a warning in the output and to stdout
but continues processing the rest.
"""

import os
from datetime import datetime

monitor_files = [
    "README.md",
    "ai-backend/.env",
    "ai-backend/app.py",
    "ai-backend/detector.py",
    "ai-backend/requirements.txt",
    "ai-backend/utils.py",
    "ai-backend/Dockerfile",
    "ai_tool.py",
    "docker-compose.yml",
    "run.sh",
    "tools.py",
    "ui-backend/.env",
    "ui-backend/app.py",
    "ui-backend/requirements.txt",
    "ui-backend/static/script.js",
    "ui-backend/static/style.css",
    "ui-backend/templates/index.html",
    "ui-backend/templates/result.html",
    "ui-backend/Dockerfile",
]

OUT_PATH = "all_code_data.txt"

def write_header(out_f, path):
    out_f.write("\n\n")
    out_f.write("=" * 80 + "\n")
    out_f.write(f"FILE: {path}\n")
    out_f.write(f"COLLECTED_AT: {datetime.utcnow().isoformat()}Z\n")
    out_f.write("=" * 80 + "\n\n")

def main():
    missing = []
    with open(OUT_PATH, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Collected code files for project\n# Generated: {datetime.utcnow().isoformat()}Z\n")
        out_f.write("# Note: missing files will be reported below\n\n")

        for file_path in monitor_files:
            write_header(out_f, file_path)

            if not os.path.exists(file_path):
                msg = f"[WARNING] File not found: {file_path}\n"
                out_f.write(msg)
                print(msg.strip())
                missing.append(file_path)
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    out_f.write(content)
            except Exception as e:
                err_msg = f"[ERROR] Failed to read {file_path}: {e}\n"
                out_f.write(err_msg)
                print(err_msg.strip())
                missing.append(file_path)

    print("\nDone. Output written to:", OUT_PATH)
    if missing:
        print("Some files were missing or unreadable:")
        for m in missing:
            print(" -", m)
    else:
        print("All files collected successfully.")

if __name__ == "__main__":
    main()
