"""
auth.py
=======
Authentication and session management for GDPR Hospital Management System.
Implements role-based access control (RBAC) with three roles:
- Admin: Full access (decrypt, anonymize, view logs)
- Doctor: View anonymized patient data only
- Receptionist: Add/edit patients, no sensitive field access

Security Features:
- Password hashing using SHA-256
- Session state management
- Role-based permissions
"""

import sqlite3
import hashlib
from typing import Optional, Dict, Tuple
from datetime import datetime


# Database path
DB_PATH = "hospital.db"


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hexadecimal hash string
        
    Note:
        In production, use bcrypt or argon2 with salt
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def login_user(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Authenticate user credentials against database.
    
    Args:
        username: User's username
        password: User's plain text password
        
    Returns:
        Tuple[bool, Optional[Dict]]: (success, user_data)
            success: True if login successful
            user_data: Dictionary with user_id, username, role
            
    Example:
        >>> success, user = login_user("admin", "admin123")
        >>> if success:
        ...     print(f"Welcome {user['username']}, Role: {user['role']}")
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Hash the provided password
        password_hash = hash_password(password)
        
        # Query user
        cursor.execute("""
            SELECT user_id, username, role
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_data = {
                'user_id': result[0],
                'username': result[1],
                'role': result[2]
            }
            print(f"✓ Login successful: {username} ({user_data['role']})")
            return True, user_data
        else:
            print(f"✗ Login failed: Invalid credentials for {username}")
            return False, None
            
    except sqlite3.Error as e:
        # Backwards compatibility: older DBs used `password` column (plaintext)
        msg = str(e)
        print(f"✗ Database error during login: {e}")
        if 'password_hash' in msg or 'no such column' in msg:
            try:
                # Try fallback: compare against legacy `password` column if present
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(users);")
                cols = [r[1] for r in cursor.fetchall()]
                if 'password' in cols:
                    cursor.execute(
                        "SELECT user_id, username, role, password FROM users WHERE username = ?",
                        (username,)
                    )
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        stored_password = row[3]
                        # Accept either plaintext legacy match or hashed match
                        if password == stored_password or hash_password(password) == stored_password:
                            user_data = {'user_id': row[0], 'username': row[1], 'role': row[2]}
                            print(f"⚠ Legacy login successful for {username} — consider migrating passwords")
                            return True, user_data
                # no fallback possible
                return False, None
            except Exception:
                return False, None
        return False, None
    except Exception as e:
        print(f"✗ Unexpected error during login: {e}")
        return False, None


def get_user_role(username: str) -> Optional[str]:
    """
    Retrieve user's role from database.
    
    Args:
        username: User's username
        
    Returns:
        Optional[str]: User role ('admin', 'doctor', 'receptionist') or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
        
    except sqlite3.Error as e:
        print(f"✗ Database error getting user role: {e}")
        return None


def verify_session(session_state) -> bool:
    """
    Verify if user session is valid.
    
    Args:
        session_state: Streamlit session state object
        
    Returns:
        bool: True if logged in, False otherwise
    """
    return (hasattr(session_state, 'logged_in') and 
            session_state.logged_in and 
            hasattr(session_state, 'user_data'))


def get_session_user(session_state) -> Optional[Dict]:
    """
    Get current user data from session.
    
    Args:
        session_state: Streamlit session state object
        
    Returns:
        Optional[Dict]: User data or None
    """
    if verify_session(session_state):
        return session_state.user_data
    return None


def init_session(session_state):
    """
    Initialize session state variables.
    
    Args:
        session_state: Streamlit session state object
    """
    if 'logged_in' not in session_state:
        session_state.logged_in = False
    if 'user_data' not in session_state:
        session_state.user_data = None


def login_session(session_state, user_data: Dict):
    """
    Set session as logged in with user data.
    
    Args:
        session_state: Streamlit session state object
        user_data: Dictionary containing user_id, username, role
    """
    session_state.logged_in = True
    session_state.user_data = user_data


def logout_session(session_state):
    """
    Clear session and logout user.
    
    Args:
        session_state: Streamlit session state object
    """
    session_state.logged_in = False
    session_state.user_data = None


def check_permission(session_state, required_role: str) -> bool:
    """
    Check if user has required permission level.
    
    Args:
        session_state: Streamlit session state object
        required_role: Required role ('admin', 'doctor', 'receptionist')
        
    Returns:
        bool: True if user has permission
        
    Role Hierarchy:
        admin > doctor > receptionist
    """
    if not verify_session(session_state):
        return False
    
    user_role = session_state.user_data.get('role', '').lower()
    required_role = required_role.lower()
    
    # Define role hierarchy
    role_levels = {
        'admin': 3,
        'doctor': 2,
        'receptionist': 1
    }
    
    user_level = role_levels.get(user_role, 0)
    required_level = role_levels.get(required_role, 0)
    
    return user_level >= required_level


def get_all_users() -> list:
    """
    Get all users from database (Admin only function).
    
    Returns:
        list: List of tuples (user_id, username, role, created_at)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, role, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        return users
        
    except sqlite3.Error as e:
        print(f"✗ Database error getting users: {e}")
        return []


def create_user(username: str, password: str, role: str) -> bool:
    """
    Create a new user (Admin only function).
    
    Args:
        username: Unique username
        password: Plain text password (will be hashed)
        role: User role ('admin', 'doctor', 'receptionist')
        
    Returns:
        bool: True if user created successfully
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✓ User created: {username} ({role})")
        return True
        
    except sqlite3.IntegrityError:
        print(f"✗ Username already exists: {username}")
        return False
    except sqlite3.Error as e:
        print(f"✗ Database error creating user: {e}")
        return False


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_authentication():
    """Test authentication system."""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION SYSTEM")
    print("="*60)
    
    # Test 1: Valid login
    print("\n[Test 1] Valid Login")
    success, user = login_user("admin", "admin123")
    assert success, "Admin login should succeed"
    assert user['role'] == 'admin', "User should be admin"
    print(f"✓ Test passed: {user}")
    
    # Test 2: Invalid login
    print("\n[Test 2] Invalid Login")
    success, user = login_user("admin", "wrongpassword")
    assert not success, "Login with wrong password should fail"
    print("✓ Test passed: Login correctly rejected")
    
    # Test 3: Get user role
    print("\n[Test 3] Get User Role")
    role = get_user_role("doctor1")
    print(f"doctor1 role: {role}")
    assert role == 'doctor', "Doctor role should be retrieved"
    print("✓ Test passed")
    
    # Test 4: Get all users
    print("\n[Test 4] Get All Users")
    users = get_all_users()
    print(f"Total users in system: {len(users)}")
    for user in users:
        print(f"  - {user[1]} ({user[2]})")
    print("✓ Test passed")
    
    # Test 5: Password hashing consistency
    print("\n[Test 5] Password Hashing")
    hash1 = hash_password("testpass123")
    hash2 = hash_password("testpass123")
    assert hash1 == hash2, "Same password should produce same hash"
    print(f"Hash: {hash1[:32]}...")
    print("✓ Test passed: Hashing is consistent")
    
    print("\n" + "="*60)
    print("✓ ALL AUTHENTICATION TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    # Run tests when executed directly
    test_authentication()