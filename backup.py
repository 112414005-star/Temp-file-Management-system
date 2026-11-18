import os
import zipfile
from pathlib import Path
from datetime import datetime


# ==========================================
# TEMP FILE ZIP BACKUP MODULE
# ==========================================

def backup_files():

    print("\n" + "=" * 60)
    print("             TEMP FILE ZIP BACKUP")
    print("=" * 60)

    # STEP 1: Get TEMP folder
    temp_folder = os.environ.get("TEMP")

    if not temp_folder or not os.path.isdir(temp_folder):
        print("[ERROR] TEMP folder not found!")
        return

    # STEP 2: Scan temporary files
    files = []

    try:
        for item in os.scandir(temp_folder):
            if item.is_file():
                files.append(item.path)

    except PermissionError:
        print("[ERROR] Permission denied!")
        return

    if not files:
        print("[INFO] No temporary files found.")
        return

    # STEP 3: Display files
    print(f"\nTotal Temporary Files Found: {len(files)}")

    print("\n" + "-" * 60)

    for index, file_path in enumerate(files, start=1):
        print(f"{index}. {os.path.basename(file_path)}")

    print("-" * 60)

    # STEP 4: Select files
    choice = input(
        "\nEnter file numbers separated by commas, "
        "or type ALL to backup all files: "
    ).strip()

    if choice.upper() == "ALL":

        selected_files = files.copy()

    else:

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

            # Remove duplicate selections
            numbers = list(dict.fromkeys(numbers))

            selected_files = [
                files[number - 1]
                for number in numbers
            ]

        except ValueError:
            print("[ERROR] Invalid input!")
            print("Enter numbers like 1,2,3 or ALL.")
            return

    # STEP 5: Create backup folder
    backup_folder = (
        Path.home() / "Documents" / "TempFileBackups"
    )

    backup_folder.mkdir(parents=True, exist_ok=True)

    # STEP 6: Create ZIP filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    zip_path = backup_folder / f"TempBackup_{timestamp}.zip"

    # STEP 7: Add selected files to ZIP
    added = 0
    skipped = 0

    print("\n[+] Creating ZIP Backup...")

    try:

        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as zip_file:

            for file_path in selected_files:

                try:
                    if os.path.isfile(file_path):
                        zip_file.write(
                            file_path,
                            arcname=os.path.basename(file_path)
                        )

                        added += 1

                    else:
                        skipped += 1

                except (PermissionError, OSError):
                    skipped += 1

    except Exception as error:
        print("[ERROR] Backup failed:", error)
        return

    # STEP 8: Final report
    print("\n" + "=" * 60)
    print("              BACKUP REPORT")
    print("=" * 60)

    print(f"Total Files Selected : {len(selected_files)}")
    print(f"Total Files Added    : {added}")
    print(f"Total Files Skipped  : {skipped}")

    if added > 0:

        print("\n[+] BACKUP SUCCESSFUL!")
        print("\nZIP File Created At:")
        print(zip_path)

    else:

        print("\n[!] No files were added to ZIP.")

        if zip_path.exists():
            zip_path.unlink()

    print("\n" + "=" * 60)

    input("\nPress Enter to return...")


# Function aliases for main.py compatibility
def main():
    backup_files()


def run_backup():
    backup_files()


if __name__ == "__main__":
    backup_files()