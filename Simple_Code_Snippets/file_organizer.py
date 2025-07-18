import os
import shutil
import hashlib
import zipfile
import rarfile
import py7zr
import datetime
import logging
import argparse
import mimetypes
import time
import json

# Placeholder for cloud storage integration
def upload_to_cloud(filepath, cloud_service, destination_path):
    """
    Placeholder function for uploading files to cloud storage.
    Replace with actual implementation for Dropbox, Google Drive, or OneDrive.
    """
    print(f"Uploading {filepath} to {cloud_service}:{destination_path}")
    time.sleep(1)  # Simulate upload time
    print(f"Successfully uploaded {filepath} to {cloud_service}:{destination_path}")
    return True

def get_file_signature(filepath, bytes_to_read=1024):
    """
    Reads the first few bytes of a file to determine its type.
    """
    try:
        with open(filepath, 'rb') as f:
            signature = f.read(bytes_to_read)
        return signature
    except Exception as e:
        logging.error(f"Error reading file signature for {filepath}: {e}")
        return None

def organize_file(filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates=False):
    """
    Organizes a single file based on specified criteria.
    """
    try:
        filename = os.path.basename(filepath)
        if sort_criteria == 'file_type':
            file_type = mimetypes.guess_type(filename)[0]
            if file_type:
                target_dir = os.path.join(destination_dir, file_type.split('/')[0])
            else:
                target_dir = os.path.join(destination_dir, 'unknown')

        elif sort_criteria == 'date_created':
            creation_time = os.path.getctime(filepath)
            date_obj = datetime.datetime.fromtimestamp(creation_time)
            target_dir = os.path.join(destination_dir, date_obj.strftime('%Y-%m-%d'))

        elif sort_criteria == 'file_size':
            file_size = os.path.getsize(filepath)
            if file_size < 1024 * 1024:  # Less than 1 MB
                target_dir = os.path.join(destination_dir, 'small')
            elif file_size < 10 * 1024 * 1024:  # Less than 10 MB
                target_dir = os.path.join(destination_dir, 'medium')
            else:
                target_dir = os.path.join(destination_dir, 'large')

        elif sort_criteria == 'file_signature':
            signature = get_file_signature(filepath)
            if signature:
                target_dir = os.path.join(destination_dir, hashlib.md5(signature).hexdigest()[:8]) # use first 8 chars of md5 hash
            else:
                target_dir = os.path.join(destination_dir, 'unknown_signature')

        elif sort_criteria == 'custom':
            target_dir = destination_dir  # Use the base destination if using custom rules.
            for rule in custom_rules:
                if rule['match_type'] == 'filename_contains' and rule['match_value'] in filename:
                    target_dir = os.path.join(destination_dir, rule['destination'])
                    break # Stop on the first match
                elif rule['match_type'] == 'file_extension' and filename.endswith(rule['match_value']):
                    target_dir = os.path.join(destination_dir, rule['destination'])
                    break


        else:
            logging.error(f"Invalid sort criteria: {sort_criteria}")
            return False

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        new_filepath = os.path.join(target_dir, filename)

        # Duplicate detection
        if remove_duplicates:
            file_hash = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
            for existing_file in os.listdir(target_dir):
                existing_filepath = os.path.join(target_dir, existing_file)
                if os.path.isfile(existing_filepath):
                    existing_file_hash = hashlib.md5(open(existing_filepath, 'rb').read()).hexdigest()
                    if file_hash == existing_file_hash:
                        logging.info(f"Duplicate file found: {filename}. Removing {filepath}")
                        os.remove(filepath)
                        return True # File was handled

        try:
            shutil.move(filepath, new_filepath)
            logging.info(f"Moved {filename} to {target_dir}")

            if cloud_service:
                cloud_destination_path = os.path.join(cloud_destination, os.path.relpath(new_filepath, destination_dir))
                if upload_to_cloud(new_filepath, cloud_service, cloud_destination_path):
                   logging.info(f"Uploaded {filename} to {cloud_service}:{cloud_destination_path}")
                else:
                    logging.error(f"Failed to upload {filename} to {cloud_service}:{cloud_destination_path}")

            return True

        except Exception as e:
            logging.error(f"Error moving {filename}: {e}")
            return False

    except Exception as e:
        logging.error(f"Error organizing {filepath}: {e}")
        return False



def handle_compressed_file(filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates):
    """
    Handles compressed files (ZIP, RAR, 7z) by extracting them to a temporary directory
    and then organizing the extracted files.
    """
    try:
        filename = os.path.basename(filepath)
        extract_dir = os.path.join(destination_dir, f".temp_{filename}")
        os.makedirs(extract_dir, exist_ok=True)

        if filepath.endswith('.zip'):
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif filepath.endswith('.rar'):
            with rarfile.RarFile(filepath, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
        elif filepath.endswith('.7z'):
            with py7zr.SevenZipFile(filepath, mode='r') as seven_zip_ref:
                seven_zip_ref.extractall(extract_dir)
        else:
            logging.warning(f"Unsupported compressed file format: {filepath}")
            return False

        # Organize the extracted files
        for root, _, files in os.walk(extract_dir):
            for file in files:
                extracted_filepath = os.path.join(root, file)
                organize_file(extracted_filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates)

        # Optionally remove the temporary directory
        shutil.rmtree(extract_dir)
        os.remove(filepath) #Remove the archive file after extracting and organizing contents

        return True

    except Exception as e:
        logging.error(f"Error handling compressed file {filepath}: {e}")
        return False


def process_directory(source_dir, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates):
    """
    Processes all files in the source directory.
    """
    try:
        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)

            if os.path.isfile(filepath):
                if filename.endswith(('.zip', '.rar', '.7z')):
                    handle_compressed_file(filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates)
                else:
                    organize_file(filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates)
            elif os.path.isdir(filepath):
                # Recursively process subdirectories (optional)
                # process_directory(filepath, destination_dir, sort_criteria, custom_rules, cloud_service, cloud_destination, remove_duplicates)
                logging.warning(f"Skipping subdirectory: {filepath}")

    except Exception as e:
        logging.error(f"Error processing directory {source_dir}: {e}")


def main():
    """
    Main function to parse arguments and start the file organization process.
    """
    parser = argparse.ArgumentParser(description="Intelligent File Organizer Script")

    parser.add_argument("source_dir", help="Source directory to organize")
    parser.add_argument("destination_dir", help="Destination directory to move files to")
    parser.add_argument("--sort_criteria", default="file_type", choices=['file_type', 'date_created', 'file_size', 'file_signature', 'custom'], help="Sorting criteria (file_type, date_created, file_size, file_signature, custom)")
    parser.add_argument("--custom_rules_file", help="Path to a JSON file containing custom sorting rules")
    parser.add_argument("--cloud_service", choices=['dropbox', 'google_drive', 'onedrive'], help="Cloud storage service to integrate with (dropbox, google_drive, onedrive)")
    parser.add_argument("--cloud_destination", default="/", help="Destination path in cloud storage")
    parser.add_argument("--remove_duplicates", action="store_true", help="Enable duplicate file detection and removal")
    parser.add_argument("--log_level", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load custom rules if specified
    custom_rules = []
    if args.sort_criteria == "custom":
        if not args.custom_rules_file:
            logging.error("Custom sorting rules require a --custom_rules_file to be specified.")
            return
        try:
            with open(args.custom_rules_file, 'r') as f:
                custom_rules = json.load(f)
        except FileNotFoundError:
            logging.error(f"Custom rules file not found: {args.custom_rules_file}")
            return
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {args.custom_rules_file}: {e}")
            return


    logging.info(f"Starting file organization from {args.source_dir} to {args.destination_dir}")
    logging.info(f"Sorting criteria: {args.sort_criteria}")
    logging.info(f"Remove duplicates: {args.remove_duplicates}")
    if args.cloud_service:
        logging.info(f"Cloud integration: {args.cloud_service} to {args.cloud_destination}")

    process_directory(args.source_dir, args.destination_dir, args.sort_criteria, custom_rules, args.cloud_service, args.cloud_destination, args.remove_duplicates)

    logging.info("File organization completed.")


if __name__ == "__main__":
    main()