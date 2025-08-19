"""
Encryption service implementation.
"""

from src.Storage.Domain.Interfaces import IEncryptionService
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class AES256EncryptionService(IEncryptionService):
    def __init__(self, key: bytes):
        """
        Initialize the AES256EncryptionService with a 32-byte key.
        
        Args:
            key: bytes
                The encryption key, must be 32 bytes long for AES-256.
        
        Raises:
            ValueError: If the key is not 32 bytes long.
        """
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long for AES-256 encryption")
        self.key = key

    def encrypt(self, data: str) -> bytes:
        """
        Encrypt the given data using AES-256 encryption.
        The key must be 32 bytes long.
        Returns the encrypted data as bytes, prefixed with the IV used for encryption.
        """
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        return bytes(cipher.iv) + ct_bytes

    def decrypt(self, data: bytes) -> str:
        """
        Decrypt the given data using AES-256 encryption.
        The data should be prefixed with the IV used for encryption.
        Returns the decrypted data as bytes.
        """
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ct), AES.block_size).decode()
