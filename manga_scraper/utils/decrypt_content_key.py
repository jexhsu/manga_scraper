# manga_scraper/utils/decrypt_content_key.py
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_content_key(content_key: str, aes_key: str, iv_length: int = 16):
    """
    Decrypt AES-CBC encrypted contentKey string consisting of IV + ciphertext (hex encoded).

    Args:
        content_key (str): Encrypted string, IV + ciphertext in hex.
        aes_key (str): AES key string (16, 24, or 32 bytes).
        iv_length (int, optional): Length of the IV prefix in characters. Default is 16.

    Returns:
        Union[dict, list]: Parsed JSON object (dict or list) after decryption.

    Raises:
        ValueError: If decryption or JSON parsing fails.
    """
    try:
        # Extract IV (initialization vector) and ciphertext from content_key
        iv_str = content_key[:iv_length]
        ciphertext_hex = content_key[iv_length:]

        # Encode IV and key to bytes
        iv = iv_str.encode("utf-8")
        key = aes_key.encode("utf-8")

        # Convert ciphertext from hex string to bytes
        ciphertext = bytes.fromhex(ciphertext_hex)

        # Create AES cipher in CBC mode with the given key and IV
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt and unpad the ciphertext
        decrypted_bytes = cipher.decrypt(ciphertext)
        decrypted_text = unpad(decrypted_bytes, AES.block_size).decode("utf-8")

        # Parse decrypted JSON string to Python object (dict or list)
        return json.loads(decrypted_text)

    except Exception as e:
        raise ValueError(f"Failed to decrypt or parse content_key: {e}")
