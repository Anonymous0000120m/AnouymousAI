import os
import sys
import logging
import argparse
import configparser
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from docx import Document

def generate_key_pair(private_key_file, public_key_file):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    with open(private_key_file, "wb") as key_file:
        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_file, "wb") as key_file:
        key_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_key_from_file(file_name):
    with open(file_name, "rb") as key_file:
        key_data = key_file.read()
        key = serialization.load_pem_private_key(key_data, password=None, backend=default_backend())
    return key

def encrypt_document(document_path, public_key, log_file):
    logging.info(f"Encrypting document: {document_path}")
    with open(document_path, 'rb') as doc_file:
        document_content = doc_file.read()

    encrypted_content = public_key.encrypt(
        document_content,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    encrypted_file_path = document_path + ".encrypted"
    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_content)

    logging.info(f"Document encrypted: {encrypted_file_path}")
    log_file.write(f"{datetime.now()} - Document encrypted: {encrypted_file_path}\n")

def decrypt_document(encrypted_document_path, private_key, log_file):
    logging.info(f"Decrypting document: {encrypted_document_path}")
    with open(encrypted_document_path, 'rb') as encrypted_file:
        encrypted_content = encrypted_file.read()

    decrypted_content = private_key.decrypt(
        encrypted_content,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    original_document_path = encrypted_document_path.replace('.encrypted', '')
    with open(original_document_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_content)

    logging.info(f"Document decrypted: {original_document_path}")
    log_file.write(f"{datetime.now()} - Document decrypted: {original_document_path}\n")

def process_documents(directory_path, key_file, log_file, action):
    if action == 'encrypt':
        logging.info("Starting encryption process.")
        public_key = load_key_from_file(key_file)
        for filename in os.listdir(directory_path):
            if filename.endswith('.doc') or filename.endswith('.docx'):
                file_path = os.path.join(directory_path, filename)
                encrypt_document(file_path, public_key, log_file)
        logging.info("Encryption process completed.")
    elif action == 'decrypt':
        logging.info("Starting decryption process.")
        private_key = load_key_from_file(key_file)
        for filename in os.listdir(directory_path):
            if filename.endswith('.encrypted'):
                file_path = os.path.join(directory_path, filename)
                decrypt_document(file_path, private_key, log_file)
        logging.info("Decryption process completed.")

def main():
    parser = argparse.ArgumentParser(description='Encrypt or decrypt documents.')
    parser.add_argument('--action', choices=['encrypt', 'decrypt'], required=True, help='Action to perform: encrypt or decrypt.')
    parser.add_argument('--directory', required=True, help='Directory path containing documents.')
    parser.add_argument('--key-file', required=True, help='Key file path (private key for decryption, public key for encryption).')
    parser.add_argument('--log-file', default='encryption.log', help='Log file path.')
    args = parser.parse_args()

    logging.basicConfig(filename=args.log_file, level=logging.INFO)

    process_documents(args.directory, args.key_file, args.log_file, args.action)

if __name__ == "__main__":
    main()
