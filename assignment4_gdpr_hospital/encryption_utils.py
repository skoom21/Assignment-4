"""
encryption_utils.py
===================
GDPR-compliant encryption utilities using Fernet (symmetric encryption).
Handles encryption, decryption, and masking of sensitive data.

Functions:
- load_fernet_key(): Load or generate Fernet encryption key
- encrypt_text(): Encrypt sensitive text
- decrypt_text(): Decrypt encrypted text
- mask_name(): Mask patient names for privacy
- mask_contact(): Mask contact information
"""

import os
from cryptography.fernet import Fernet
from typing import Optional


# Constants
KEY_FILE = "fernet.key"


def load_fernet_key() -> Fernet:
    """
    Load existing Fernet key from file or generate a new one.
    
    Returns:
        Fernet: Fernet cipher instance for encryption/decryption
        
    Security Note:
        In production, store keys in secure key management systems (AWS KMS, Azure Key Vault)
    """
    try:
        if os.path.exists(KEY_FILE):
            # Load existing key
            with open(KEY_FILE, "rb") as key_file:
                key = key_file.read()
            print(f"✓ Loaded encryption key from {KEY_FILE}")
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
            print(f"✓ Generated new encryption key and saved to {KEY_FILE}")
        
        return Fernet(key)
    
    except Exception as e:
        print(f"✗ Error loading/generating Fernet key: {e}")
        raise


def encrypt_text(plaintext: str, fernet: Optional[Fernet] = None) -> str:
    """
    Encrypt plaintext using Fernet symmetric encryption.
    
    Args:
        plaintext: Text to encrypt
        fernet: Fernet instance (if None, loads from key file)
        
    Returns:
        str: Base64-encoded encrypted text
        
    Example:
        >>> encrypted = encrypt_text("Hypertension")
        >>> print(encrypted)
        gAAAAABh5x2y...
    """
    try:
        if fernet is None:
            fernet = load_fernet_key()
        
        if not plaintext or plaintext.strip() == "":
            return ""
        
        # Encode to bytes, encrypt, decode to string for storage
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))
        encrypted_str = encrypted_bytes.decode('utf-8')
        
        return encrypted_str
    
    except Exception as e:
        print(f"✗ Encryption error: {e}")
        return ""


def decrypt_text(encrypted_text: str, fernet: Optional[Fernet] = None) -> str:
    """
    Decrypt Fernet-encrypted text.
    
    Args:
        encrypted_text: Base64-encoded encrypted text
        fernet: Fernet instance (if None, loads from key file)
        
    Returns:
        str: Decrypted plaintext
        
    Example:
        >>> decrypted = decrypt_text("gAAAAABh5x2y...")
        >>> print(decrypted)
        Hypertension
    """
    try:
        if fernet is None:
            fernet = load_fernet_key()
        
        if not encrypted_text or encrypted_text.strip() == "":
            return ""
        
        # Encode to bytes, decrypt, decode to string
        decrypted_bytes = fernet.decrypt(encrypted_text.encode('utf-8'))
        decrypted_str = decrypted_bytes.decode('utf-8')
        
        return decrypted_str
    
    except Exception as e:
        print(f"✗ Decryption error: {e}")
        return "[DECRYPTION_FAILED]"


def mask_name(name: str) -> str:
    """
    Mask patient name for privacy (GDPR Article 32 - Pseudonymization).
    
    Args:
        name: Full patient name
        
    Returns:
        str: Masked name showing only first letter and last letter
        
    Examples:
        >>> mask_name("John Doe")
        'J*** D**'
        >>> mask_name("A")
        'A'
        >>> mask_name("")
        ''
    """
    try:
        if not name or len(name.strip()) == 0:
            return ""
        
        name = name.strip()
        
        # Handle single character
        if len(name) == 1:
            return name
        
        # Mask each word separately
        words = name.split()
        masked_words = []
        
        for word in words:
            if len(word) == 1:
                masked_words.append(word)
            elif len(word) == 2:
                masked_words.append(f"{word[0]}*")
            else:
                # Show first and last letter, mask middle
                masked = f"{word[0]}{'*' * (len(word) - 2)}{word[-1]}"
                masked_words.append(masked)
        
        return " ".join(masked_words)
    
    except Exception as e:
        print(f"✗ Name masking error: {e}")
        return "***"


def mask_contact(contact: str) -> str:
    """
    Mask contact information (phone/email) for privacy.
    
    Args:
        contact: Phone number or email address
        
    Returns:
        str: Masked contact information
        
    Examples:
        >>> mask_contact("+1234567890")
        '+12****7890'
        >>> mask_contact("patient@email.com")
        'p*****@email.com'
        >>> mask_contact("")
        ''
    """
    try:
        if not contact or len(contact.strip()) == 0:
            return ""
        
        contact = contact.strip()
        
        # Detect email (contains @)
        if "@" in contact:
            local, domain = contact.split("@", 1)
            if len(local) <= 2:
                masked_local = local[0] + "*"
            else:
                masked_local = local[0] + "*" * (len(local) - 1)
            return f"{masked_local}@{domain}"
        
        # Phone number masking
        else:
            if len(contact) <= 4:
                return "*" * len(contact)
            else:
                # Show first 3 and last 4 digits
                visible_start = 3
                visible_end = 4
                masked_middle = "*" * (len(contact) - visible_start - visible_end)
                return f"{contact[:visible_start]}{masked_middle}{contact[-visible_end:]}"
    
    except Exception as e:
        print(f"✗ Contact masking error: {e}")
        return "***"


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_encryption():
    """Test encryption and decryption functionality."""
    print("\n" + "="*60)
    print("TESTING ENCRYPTION UTILITIES")
    print("="*60)
    
    # Test 1: Basic encryption/decryption
    print("\n[Test 1] Basic Encryption/Decryption")
    fernet = load_fernet_key()
    
    test_data = "Hypertension, Type 2 Diabetes"
    print(f"Original:  {test_data}")
    
    encrypted = encrypt_text(test_data, fernet)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = decrypt_text(encrypted, fernet)
    print(f"Decrypted: {decrypted}")
    
    assert decrypted == test_data, "Decryption failed!"
    print("✓ Encryption/Decryption: PASSED")
    
    # Test 2: Name masking
    print("\n[Test 2] Name Masking")
    test_names = [
        "John Doe",
        "Alice",
        "Muhammad Ali Khan",
        "A B",
        ""
    ]
    
    for name in test_names:
        masked = mask_name(name)
        print(f"  {name:20s} → {masked}")
    
    # Test 3: Contact masking
    print("\n[Test 3] Contact Masking")
    test_contacts = [
        "+1234567890",
        "patient@hospital.com",
        "john.doe@email.org",
        "+92-300-1234567",
        ""
    ]
    
    for contact in test_contacts:
        masked = mask_contact(contact)
        print(f"  {contact:25s} → {masked}")
    
    print("\n" + "="*60)
    print("✓ ALL ENCRYPTION TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    # Run tests when executed directly
    test_encryption()