import os
from pathlib import Path


# ==========================================
# TEMP FILE DELETE MODULE
# ==========================================

def delete_files():

    print("\n" + "=" * 60)
    print("              TEMP FILE DELETE")
    print("=" * 60)

    # STEP 1: Get TEMP folder
    temp_folder = os.environ.get("TEMP")

    if not temp_folder or not os.path.isdir(temp_folder):
        print("[ERROR] TEMP folder not found!")
        return

    # STEP 2: Scan files
    files = []

    try:
        with os.scandir(temp_folder) as entries:
            for item in entries:
                if item.is_file(follow_symlinks=False):
                    files.append(item.path)

    except OSError as error:
        print("[ERROR] Scan failed:", error)
        return

    if not files:
        print("\nNo temporary files found!")
        return

    # STEP 3: Display files
    print(f"\nTotal Files Found: {len(files)}")

    for index, file_path in enumerate(files, 1):
        print(f"{index}. {os.path.basename(file_path)}")

    # STEP 4: Select files
    choice = input(
        "\nEnter file numbers separated by commas: "
    ).strip()

    try:
        numbers = [
            int(value.strip())
            for value in choice.split(",")
        ]

        if not numbers:
            print("[ERROR] No files selected!")
            return

        if any(number < 1 or number > len(files)
               for number in numbers):
            print("[ERROR] Invalid file number!")
            return

        numbers = list(dict.fromkeys(numbers))

    except ValueError:
        print("[ERROR] Invalid input!")
        return

    selected_files = [
        files[number - 1]
        for number in numbers
    ]

    # STEP 5: Confirmation
    print("\nSelected Files:")

    for file_path in selected_files:
        print(os.path.basename(file_path))

    confirm = input(
        "\nConfirm deletion? (YES/NO): "
    ).strip().upper()

    if confirm != "YES":
        print("\nDeletion Cancelled!")
        return

    # STEP 6: Delete selected files
    deleted = 0
    skipped = 0

    for file_path in selected_files:

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted += 1
            else:
                skipped += 1

        except (PermissionError, OSError):
            skipped += 1

    # STEP 7: Final Report
    print("\n" + "=" * 60)
    print("              DELETE REPORT")
    print("=" * 60)

    print(f"Selected Files : {len(selected_files)}")
    print(f"Deleted Files  : {deleted}")
    print(f"Skipped Files  : {skipped}")

    print("\nDELETE OPERATION COMPLETED!")

    print("=" * 60)

    input("\nPress Enter to return...")


def main():
    delete_files()


if __name__ == "__main__":
    delete_files()