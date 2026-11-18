import os

# Get TEMP folder
temp_folder = os.environ.get("TEMP")

# Store files
files = []

# Scan TEMP folder
for item in os.listdir(temp_folder):

    path = os.path.join(temp_folder, item)

    if os.path.isfile(path):
        files.append(path)

print("=" * 60)
print("          TEMP FILE SELECTION")
print("=" * 60)

print("\nTotal files available:", len(files))

print("\nEnter the file numbers you want to manage.")
print("Example: 1,5,8")

choice = input("\nEnter file numbers: ")

try:

    numbers = [int(x.strip()) for x in choice.split(",")]

    selected_files = []

    for number in numbers:

        if 1 <= number <= len(files):

            selected_files.append(files[number - 1])

        else:

            print(number, "is not a valid file number.")

    print("\nSELECTED FILES")
    print("-" * 60)

    for number, file_path in zip(numbers, selected_files):

        file_name = os.path.basename(file_path)

        print(number, ".", file_name)

    print("\nTotal selected:", len(selected_files))

except ValueError:

    print("\nInvalid input. Please enter numbers only.")