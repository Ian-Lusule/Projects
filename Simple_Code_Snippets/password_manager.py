import secrets
import string
import hashlib
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import pyotp
import time
import requests
import webbrowser

# Password Generation
def generate_password(length=16, include_digits=True, include_symbols=True, include_lowercase=True, include_uppercase=True):
    characters = ""
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_digits:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    if not characters:
        return "Error: At least one character set must be selected."

    return ''.join(secrets.choice(characters) for _ in range(length))

# Encryption/Decryption using Fernet (AES)
def generate_key(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a new salt if none is provided
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,  # Increased iteration count
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

# Password Storage (JSON File) - Simplified
def save_password(category, account, password, master_password, filename="passwords.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    if category not in data:
        data[category] = {}
    
    if account in data[category]:
        print(f"Warning: Account '{account}' already exists in category '{category}'. Overwriting.")

    key, salt = generate_key(master_password)
    encrypted_password = encrypt_data(password, key)

    if 'metadata' not in data[category]:
        data[category]['metadata'] = {}
    
    data[category]['metadata'][account] = {'salt': base64.b64encode(salt).decode()} # Store salt
    data[category][account] = base64.b64encode(encrypted_password).decode() #Base64 encode encrypted data

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Password saved for {account} in {category}.")

def retrieve_password(category, account, master_password, filename="passwords.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return None

    if category not in data or account not in data[category]:
        return None
    
    if 'metadata' not in data[category] or account not in data[category]['metadata']:
        print("Warning: No salt found for this password. Possible data corruption.")
        return None  # Unable to decrypt without the salt

    salt = base64.b64decode(data[category]['metadata'][account]['salt'])
    key, _ = generate_key(master_password, salt)
    encrypted_password_b64 = data[category][account] #Get the base64 encoded password
    encrypted_password = base64.b64decode(encrypted_password_b64)  # decode back to bytes

    try:
        decrypted_password = decrypt_data(encrypted_password, key)
        return decrypted_password
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

# TOTP Implementation
def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, account_name, issuer_name):
    return pyotp.TOTP(secret).provisioning_uri(name=account_name, issuer_name=issuer_name)

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

# Password Strength Testing (Simplified)
def test_password_strength(password):
    length = len(password)
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_symbols = any(c in string.punctuation for c in password)

    score = 0
    if length >= 8:
        score += 25
    if has_lowercase:
        score += 25
    if has_uppercase:
        score += 25
    if has_digits:
        score += 15
    if has_symbols:
        score += 10

    if score >= 80:
        return "Strong"
    elif score >= 60:
        return "Medium"
    else:
        return "Weak"

# Have I Been Pwned Integration (Password Breach Monitoring)
def check_password_pwned(password):
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)
    
    if response.status_code == 200:
        for line in response.text.splitlines():
            hash_suffix, count = line.split(":")
            if hash_suffix == suffix:
                return int(count)
        return 0  # Not found
    else:
        print(f"Error checking Have I Been Pwned: {response.status_code}")
        return -1

# Simple CLI Interface
def cli_interface():
    while True:
        print("\nPassword Manager Menu:")
        print("1. Generate Password")
        print("2. Save Password")
        print("3. Retrieve Password")
        print("4. Test Password Strength")
        print("5. Check Password Breach (Have I Been Pwned)")
        print("6. Generate TOTP Secret and URI")
        print("7. Verify TOTP")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            length = int(input("Enter password length: "))
            include_digits = input("Include digits? (y/n): ").lower() == 'y'
            include_symbols = input("Include symbols? (y/n): ").lower() == 'y'
            include_lowercase = input("Include lowercase? (y/n): ").lower() == 'y'
            include_uppercase = input("Include uppercase? (y/n): ").lower() == 'y'
            password = generate_password(length, include_digits, include_symbols, include_lowercase, include_uppercase)
            print(f"Generated Password: {password}")

        elif choice == '2':
            category = input("Enter category: ")
            account = input("Enter account name: ")
            password = input("Enter password: ")
            master_password = input("Enter master password: ")
            save_password(category, account, password, master_password)

        elif choice == '3':
            category = input("Enter category: ")
            account = input("Enter account name: ")
            master_password = input("Enter master password: ")
            password = retrieve_password(category, account, master_password)
            if password:
                print(f"Password: {password}")
            else:
                print("Password not found.")

        elif choice == '4':
            password = input("Enter password to test: ")
            strength = test_password_strength(password)
            print(f"Password Strength: {strength}")

        elif choice == '5':
            password = input("Enter password to check for breaches: ")
            pwned_count = check_password_pwned(password)
            if pwned_count == -1:
                print("Error checking password breaches.")
            elif pwned_count == 0:
                print("Password not found in any breaches.")
            else:
                print(f"Password has been pwned {pwned_count} times.")

        elif choice == '6':
            secret = generate_totp_secret()
            account_name = input("Enter account name for TOTP: ")
            issuer_name = input("Enter issuer name for TOTP: ")
            uri = get_totp_uri(secret, account_name, issuer_name)
            print(f"TOTP Secret: {secret}")
            print(f"TOTP URI: {uri}")
            print("You can use this URI with a TOTP authenticator app.")

        elif choice == '7':
            secret = input("Enter TOTP secret: ")
            token = input("Enter TOTP token: ")
            if verify_totp(secret, token):
                print("TOTP verification successful.")
            else:
                print("TOTP verification failed.")

        elif choice == '8':
            print("Exiting.")
            break

        else:
            print("Invalid choice. Please try again.")
# Browser Extension (Placeholder - Requires Browser Extension Development)
def browser_extension_integration():
    print("Browser extension functionality would be implemented here.")
    print("This would involve creating a browser extension that communicates with the password manager.")
    print("The extension would allow automatic filling of passwords in web browsers.")
    print("Requires browser-specific extension development (e.g., Chrome, Firefox).")

if __name__ == "__main__":
    cli_interface()