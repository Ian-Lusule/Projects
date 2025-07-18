import os
import shutil
import argparse

def organize_files(directory, extensions):
    """Organizes files in a directory based on their extensions."""

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            base, ext = os.path.splitext(filename)
            ext = ext.lower()[1:]  # remove leading dot and lowercase

            if ext in extensions:
                folder_name = extensions[ext]
                folder_path = os.path.join(directory, folder_name)

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                destination = os.path.join(folder_path, filename)
                shutil.move(filepath, destination)
            

def main():
    parser = argparse.ArgumentParser(description="Organize files in a directory.")
    parser.add_argument("directory", help="The directory to organize.")
    parser.add_argument("-e", "--extensions", nargs="+", help="File extensions and their corresponding folder names (e.g., '.txt' 'Documents', '.jpg' 'Images')")

    args = parser.parse_args()

    if args.extensions:
        extensions_dict = dict(zip(args.extensions[::2], args.extensions[1::2]))
        organize_files(args.directory, extensions_dict)
    else:
        print("Please specify file extensions and folder names using the -e option.")


if __name__ == "__main__":
    main()
