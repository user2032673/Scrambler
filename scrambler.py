import os
import datetime
import gzip
import io
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from getpass import getpass
import argparse

parser = argparse.ArgumentParser(prog='scrambler.py', description='Encrypt or decrypt a file with AES-SIV-512 using an Scrypt derived key', epilog='WARNING: ALWAYS BE CAUTIOUS WITH CRYPTOGRAPHY. IF YOU LOSE THE KEY, YOU CANNOT DECRYPT ANY FILES.')
parser.add_argument("input", help="Input file to read from")
parser.add_argument("output", help="Output file to write to")
operation_group = parser.add_mutually_exclusive_group(required=True)
operation_group.add_argument('--encrypt', action='store_true', help='Encrypt the input file and write ciphertext to the output file')
operation_group.add_argument('--decrypt', action='store_true', help='Decrypt the input file and write plaintext to the output file')

args = parser.parse_args()
file = args.input
file_output = args.output

if not os.path.exists(args.input):
    print(f'Input file nonexistent!')
    raise SystemExit

if os.path.exists(args.output):
    print(f'WARNING: Specified output file already exists. Continuing could overwrite it.')
    while True:
        choice = input(f'Are you sure you want to continue? [Y/N] ')
        if choice.strip().lower() not in ['y', 'n']:
            print('Invalid choice.')
            continue
        if choice.strip().lower() == 'y':
            print('OK, continuing at your own risk!')
            break
        if choice.strip().lower() == 'n':
            raise SystemExit


if args.encrypt:
    print('Please note that you will not see your password as it is being typed. This is a shoulder surfing prevention.')
    print('Do ensure your password is typed as you intend, as without it you cannot recover the plaintext!')
    password = ''
    confirmation = None
    while password != confirmation:
        password = getpass('Password: ')
        confirmation = getpass('Confirm Password: ')
        if password != confirmation:
            print('Password and confirmation did not match.')
    salt = os.urandom(32)
    kdf = Scrypt(salt=salt, length=64, n=2**17, r=8, p=4)
    print('Deriving key - please wait, may take a while . . .')
    key = kdf.derive(password.encode())
    encryptor = AESSIV(key)
    print('Reading input data . . .')
    with open(file, 'rb') as fileHandle:
        data = fileHandle.read()
    out = io.BytesIO()
    print('Compressing plaintext . . .')
    with gzip.GzipFile(fileobj=out, mode='wb') as gz_file:
        gz_file.write(data)
    compressed_data = out.getvalue()
    timestamp = str(round(datetime.datetime.now().timestamp())).encode()
    aad = [timestamp]
    print('Encrypting data . . .')
    ciphertext = encryptor.encrypt(compressed_data, aad)
    print('Saving ciphertext . . .')
    with open(file_output, 'wb') as fileHandle:
        fileHandle.write(timestamp + b'|' + salt + b'|' + ciphertext)
    print('Encryption done.')


elif args.decrypt:
    print('Reading ciphertext . . .')
    with open(file, 'rb') as fileHandle:
        data = fileHandle.read()
    timestamp, remaining = data.split(b'|', 1)
    salt, ciphertext = remaining.split(b'|', 1)
    print('Please note that you will not see your password as it is being typed. This is a shoulder surfing prevention.')
    password = getpass('Password: ')
    kdf = Scrypt(salt=salt, length=64, n=2**17, r=8, p=4)
    print('Deriving key - please wait, may take a while . . .')
    key = kdf.derive(password.encode())
    decryptor = AESSIV(key)
    aad = [timestamp]
    try:
        print('Decrypting ciphertext . . .')
        compressed_plaintext = decryptor.decrypt(ciphertext, aad)
        in_ = io.BytesIO(compressed_plaintext)
        print('Decompressing plaintext . . .')
        with gzip.GzipFile(fileobj=in_, mode='rb') as gz_file:
            plaintext = gz_file.read()
        print('Saving plaintext . . .')
        with open(file_output, 'wb') as fileHandle:
            fileHandle.write(plaintext)
        print(f"Timestamp of encryption: {timestamp.decode()}")
        print('Decryption done.')
    except Exception as e:
        print(f"Decryption failed. Your password might be wrong, or the ciphertext might have been tampered with.")
