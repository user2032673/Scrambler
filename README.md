# Scrambler
A simple cryptography tool, to protect your data. Uses AES-SIV-512 with a key derived from Scrypt. Careful not to lose your keys!

## Quickstart

This section details how to run the executable from a command line shell. 

For Windows:
Grab scrambler.exe, either from the Github release or from scrambler.exe in the repository.
Now, open a Command Prompt on your machine, and run 
cd Downloads
if you've downloaded scrambler.exe to your Downloads. Then, pick a file in File Explorer, right click it, and select Copy as Path. This is the plaintext file you want to encrypt.
In your Command Prompt, go ahead and run
scrambler.exe --encrypt yourPath encrypted_file.bin
Make sure to replace yourPath with the path you copied, for example:
"C:\Users\Username\Desktop\sensitive_file.pdf"
including quotes. If you right clicked and copied as path earlier, you can paste it in by right clicking.
Now, enter an encryption password, and confirm it. This can be anything, but you must use the same password during decryption.
It may look like the program hangs for a moment, but this is most likely key derivation, as the KDF used(Scrypt) is intentionally memory and CPU hard to deter brute force attackers.
Once done, your encrypted file is saved to your Downloads folder as "encrypted_file.bin". This file can now be distributed globally, and no one can view the contents without the password.
Do be aware that an attacker can see the timestamp of encryption(when your files were encrypted), but they cannot modify said timestamp.

Now, to decrypt said encrypted file, place encrypted_file.bin in your Downloads, and run
scrambler.exe --decrypt encrypted_file.bin output.bin
Enter the same password used during encryption, and wait for your file to decrypt.
If it aborts for a wrong password, either you've entered an incorrect password or an attacker has tampered with the encrypted file.
If it suceeds, a byte-for-byte copy of the original file will be written to output.bin, which can then be renamed to your original file extension(pdf, jpg, mp3) and used like the original file.

Encryption and decryption do not need to occur on the same machine - the encrypted file can be decrypted anywhere, provided you have the password.


If you are unable to see file name extensions, you may need to enable it in File Explorer.

## Cryptography

The crypto behind this is fairly high-level, not really working with primitives. AES-SIV-512 is used to encrypt the files, and it's symmetric encryption with a "synthetic initialization vector". Therefore, IV management isn't a concern unlike in GCM mode.

The key is derived from Scrypt, a memory hard hashing algorithm. Specifically, the tool uses a salt length of 32 bytes, an output length of 64 bytes, an iteration count of 2^17 or 131072, a block size of 8, and a parallelism factor of 4.

The timestamp at which the file is encrypted is prepended to the ciphertext, but also included in the AAD, so an attacker can't just replace the file with an earlier one under the same key and avoid detection. 

If the attacker spoofs the timestamp, the AAD will be invalid during decryption.
