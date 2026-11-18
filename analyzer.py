import os
import traceback
from datetime import datetime

# ==========================================
# TEMPORARY FILE ANALYZER
# ==========================================

def analyze_temp_files():

    # Get User TEMP folder
    temp_folder = os.environ.get("TEMP")

    print("=" * 60)
    print("        TEMPORARY FILE ANALYZER")
    print("=" * 60)

    print("\nTEMP Folder:")
    print(temp_folder)

    # Check TEMP folder
    if not temp_folder or not os.path.isdir(temp_folder):
        print("\nTEMP folder not found!")
        return

    # Store files
    files = []

    print("\nScanning temporary files...\n")

    # Scan TEMP folder
    try:
        with os.scandir(temp_folder) as entries:

            for item in entries:

                if item.is_file(follow_symlinks=False):

                    try:
                        file_path = item.path
                        info = item.stat(follow_symlinks=False)

                        files.append({
                            "name": item.name,
                            "path": file_path,
                            "size": info.st_size,
                            "type": os.path.splitext(item.name)[1] or "No Extension",
                            "modified": datetime.fromtimestamp(info.st_mtime)
                        })

                    except (PermissionError, OSError) as error:
                        print("Skipped:", item.name)
                        print("Reason:", error)

    except (PermissionError, OSError) as error:
        print("\nScanning error:", error)
        return

    # Display total files
    print("\nTotal files found:", len(files))

    print("\nFILE DETAILS")
    print("-" * 60)

    total_size = 0

    # Analyze each file
    for number, file in enumerate(files, start=1):

        total_size += file["size"]

        print("\nFile No:", number)
        print("Name:", file["name"])
        print("Size:", file["size"], "bytes")
        print("Type:", file["type"])
        print("Path:", file["path"])
        print("Modified:", file["modified"])

    # Summary
    print("\n" + "=" * 60)
    print("              ANALYSIS SUMMARY")
    print("=" * 60)

    print("\nTotal Files:", len(files))
    print("Total Size:", total_size, "bytes")
    print("Total Size:", round(total_size / (1024 * 1024), 2), "MB")

    # File type analysis
    file_types = {}

    for file in files:
        extension = file["type"]
        file_types[extension] = file_types.get(extension, 0) + 1

    print("\nFILE TYPE SUMMARY")
    print("-" * 60)

    for extension, count in sorted(file_types.items()):
        print(extension, ":", count, "files")

    print("\n" + "=" * 60)
    print("       FILE ANALYSIS COMPLETED")
    print("=" * 60)


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    try:
        analyze_temp_files()

    except Exception:
        print("\nUnexpected error:")
        traceback.print_exc()

    finally:
        input("\nPress ENTER to close the Analyzer...")
        