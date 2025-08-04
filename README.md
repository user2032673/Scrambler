# Scrambler
A simple cryptography tool, to protect your data. Uses AES-SIV-512 with a key derived from Scrypt. Careful not to lose your keys!

## Cryptography

The crypto behind this is fairly high-level. AES-SIV-512 is used to encrypt the files, and it's symmetric encryption with a "synthetic initialization vector". Therefore, IV management isn't a concern unlike in GCM mode.
The key is derived from Scrypt, a memory hard hashing algorithm. Specifically, the tool uses a salt length of 32 bytes, an output length of 64 bytes, an iteration count of 2^17 or 131072, a block size of 8, and a parallelism factor of 4.
The timestamp at which the file is encrypted is prepended to the ciphertext, but also included in the AAD, so an attacker can't just replace the file with an earlier one under the same key and avoid detection. If the attacker spoofs the timestamp, the AAD will be invalid during decryption.
