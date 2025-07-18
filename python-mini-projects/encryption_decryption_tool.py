import base64

def encrypt(message, key):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    encrypted_message = ""
    for i in range(len(base64_message)):
        char = base64_message[i]
        encrypted_char = chr(((ord(char) + key - 32) % 94) + 32)
        encrypted_message += encrypted_char
    return encrypted_message

def decrypt(encrypted_message, key):
    decrypted_message = ""
    for i in range(len(encrypted_message)):
        char = encrypted_message[i]
        decrypted_char = chr(((ord(char) - key - 32) % 94) + 32)
        decrypted_message += decrypted_char
    base64_decrypted = "".join(decrypted_message)
    base64_bytes = base64_decrypted.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message

while True:
    print("Select an operation:")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Exit")

    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        message = input("Enter message to encrypt: ")
        key = int(input("Enter encryption key (integer): "))
        encrypted_message = encrypt(message, key)
        print("Encrypted message:", encrypted_message)
    elif choice == '2':
        encrypted_message = input("Enter message to decrypt: ")
        key = int(input("Enter decryption key (integer): "))
        decrypted_message = decrypt(encrypted_message, key)
        print("Decrypted message:", decrypted_message)
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please try again.")

