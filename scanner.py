
import os
import traceback
from datetime import datetime


def scan_temp_files():
    temp_folder = os.environ.get("TEMP")

    print("\n" + "=" * 60)
    print("          TEMPORARY FILE SCANNER")
    print("=" * 60)

    print("\nTEMP Folder:", temp_folder)

    if not temp_folder or not os.path.isdir(temp_folder):
        print("\nERROR: TEMP folder not found!")
        return

    files = []

    print("\nScanning temporary files... Please wait.\n")

    try:
        with os.scandir(temp_folder) as entries:
            for item in entries:

                if not item.is_file(follow_symlinks=False):
                    continue

                try:
                    info = item.stat(follow_symlinks=False)

                    file_name = item.name
                    file_path = item.path
                    file_size = info.st_size
                    file_type = os.path.splitext(file_name)[1]

                    if not file_type:
                        file_type = "No Extension"

                    modified = datetime.fromtimestamp(info.st_mtime)

                    files.append({
                        "name": file_name,
                        "path": file_path,
                        "size": file_size,
                        "type": file_type,
                        "modified": modified
                    })

                except (PermissionError, OSError):
                    print("Skipped:", item.name)

    except Exception as error:
        print("\nScanning error:", error)
        return

    # Display scan results
    print("\n" + "=" * 60)
    print("                  SCAN RESULTS")
    print("=" * 60)

    print("\nTotal temporary files found:", len(files))

    if not files:
        print("\nNo temporary files found.")
        return

    print("\nFILE DETAILS")
    print("-" * 60)

    for number, file in enumerate(files, start=1):
        print(f"\n[{number}] {file['name']}")
        print(" Type     :", file["type"])
        print(" Size     :", file["size"], "bytes")
        print(" Modified :", file["modified"])
        print(" Path     :", file["path"])

    # File selection
    print("\n" + "=" * 60)
    print("                 FILE SELECTION")
    print("=" * 60)

    print("\nEnter file numbers separated by commas.")
    print("Example: 1,3,5")
    print("Type ALL to select every file.")

    selection = input("\nEnter your selection: ").strip()

    selected_files = []

    if selection.lower() == "all":
        selected_files = files.copy()

    elif selection:
        try:
            numbers = set()

            for value in selection.split(","):
                value = value.strip()

                if not value:
                    continue

                index = int(value)

                if 1 <= index <= len(files):
                    numbers.add(index)
                else:
                    print("Invalid file number:", index)

            selected_files = [
                files[index - 1]
                for index in sorted(numbers)
            ]

        except ValueError:
            print("\nInvalid input! Enter numbers or ALL.")

    # Display selected files
    print("\n" + "=" * 60)
    print("                 SELECTED FILES")
    print("=" * 60)

    if selected_files:
        for number, file in enumerate(selected_files, start=1):
            print(f"{number}. {file['name']}")

        print("\nTotal selected:", len(selected_files))
    else:
        print("\nNo files selected.")

    print("\n" + "=" * 60)
    print("                 SCAN COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        scan_temp_files()

    except Exception:
        print("\nUNEXPECTED ERROR:")
        traceback.print_exc()

    finally:
        input("\nPress ENTER to close the scanner...")
