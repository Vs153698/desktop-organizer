import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS

# Define file types and their corresponding extensions
FILE_TYPES = {
    "Images": [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".ico", ".svg", ".webp", ".heic", ".heif", ".avif", ".raw", ".psd", ".ai", ".eps", ".indd", ".raw", ".arw", ".cr2", ".crw", ".dng", ".erf", ".heic", ".jfif", ".kdc", ".mrw", ".nef", ".nrw", ".orf", ".pef", ".ptx", ".pxn", ".raf", ".raw", ".rwl", ],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".md",],
    "Audio": [".mp3", ".wav", ".wma", ".aac", ".flac", ".m4a", ".ogg"],
    "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Executables": [".exe", ".msi", ".apk", ".app", ".dmg", ".pkg", ".deb", ".rpm", ".jar", ".bat", ".cmd"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "Scripts": [".js", ".py", ".sh", ".bat", ".cmd", ".ps1", ".vbs", ".rb", ".pl", ".php", ".cs", ".java", ".go", ".swift", ".dart", ".kt", ".ts"],
    "Misc": [".html", ".xml", ".json", ".yaml", ".log", ".md", ".csv", ".ini", ".db", ".sql", ".sqlite", ".db", ".db3", ".db4", ".db5", ".db6", ".db7", ".db8", ".db9", ".db10", ".db11", ".db12", ".db13", ".db14", ".db15", ".db16", ".db17", ]
}

# File size categories in MB
SIZE_CATEGORIES = {
    "Small_Files": 10,    # < 10 MB
    "Medium_Files": 500,  # 10 MB to 500 MB
    "Large_Files": 2048,  # 500 MB to 2 GB
    "Extra_Large_Files": float('inf')  # > 2 GB (infinity to cover any larger files)
}


# Get the size of a file in MB
def get_size_in_mb(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

# Function to move files based on size
def move_file_by_size(file_path, dest_folder, folder_name):
    """Create the folder and move the file."""
    size_category_path = os.path.join(dest_folder, folder_name)
    os.makedirs(size_category_path, exist_ok=True)
    shutil.move(file_path, os.path.join(size_category_path, os.path.basename(file_path)))

# Function to organize files and folders
def organize_files(src_folder, dest_folder):
    try:
        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)

            # If it's a folder, move it to the "Folders" category
            if os.path.isdir(src_path):
                dest_path = os.path.join(dest_folder, "Folders")
                os.makedirs(dest_path, exist_ok=True)
                shutil.move(src_path, os.path.join(dest_path, item))

            # If it's a file, categorize based on extension and size
            elif os.path.isfile(src_path):
                file_ext = os.path.splitext(item)[1].lower()
                file_size = get_size_in_mb(src_path)

                folder_found = False
                # Categorize files by extension
                for folder, extensions in FILE_TYPES.items():
                    if file_ext in extensions:
                        folder_found = True
                        file_type_dest_path = os.path.join(dest_folder, folder)
                        os.makedirs(file_type_dest_path, exist_ok=True)
                        
                        # Categorize by size within the extension-based folder
                        if file_size < SIZE_CATEGORIES["Small_Files"]:
                            move_file_by_size(src_path, file_type_dest_path, "Small_Files")
                        elif file_size < SIZE_CATEGORIES["Medium_Files"]:
                            move_file_by_size(src_path, file_type_dest_path, "Medium_Files")
                        elif file_size < SIZE_CATEGORIES["Large_Files"]:
                            move_file_by_size(src_path, file_type_dest_path, "Large_Files")
                        else:
                            move_file_by_size(src_path, file_type_dest_path, "Extra_Large_Files")
                        break

                # If no matching extension, move to "Others"
                if not folder_found:
                    others_dest_path = os.path.join(dest_folder, "Others")
                    os.makedirs(others_dest_path, exist_ok=True)
                    
                    # Categorize by size within the "Others" folder
                    if file_size < SIZE_CATEGORIES["Small_Files"]:
                        move_file_by_size(src_path, others_dest_path, "Small_Files")
                    elif file_size < SIZE_CATEGORIES["Medium_Files"]:
                        move_file_by_size(src_path, others_dest_path, "Medium_Files")
                    elif file_size < SIZE_CATEGORIES["Large_Files"]:
                        move_file_by_size(src_path, others_dest_path, "Large_Files")
                    else:
                        move_file_by_size(src_path, others_dest_path, "Extra_Large_Files")

        return {"status": "success", "message": "Files and folders organized successfully by type and size"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Flask API for Electron to interact with
app = Flask(__name__)
CORS(app)


@app.route('/organize', methods=['POST'])
def organize():
    data = request.get_json()
    src_folder = data['srcFolder']
    dest_folder = data['destFolder']
    print(f"Source: {src_folder}, Destination: {dest_folder}")
    result = organize_files(src_folder, dest_folder)
    return jsonify(result)

import os

if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG", "False") == "True")  # Use environment variable to control debug mode


