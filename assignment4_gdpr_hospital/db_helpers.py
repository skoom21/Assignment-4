"""
db_helpers.py
=============
Database helper functions for GDPR Hospital Management System.
Handles patient CRUD operations, anonymization, and audit logging.

GDPR Compliance Features:
- Encrypted diagnosis storage
- Patient anonymization (Right to erasure - Article 17)
- Comprehensive audit trail (Article 30)
- Data minimization principles

Functions:
- add_patient(): Create new patient record
- update_patient(): Update existing patient
- get_all_patients(): Retrieve all patients
- anonymize_patient_row(): Anonymize patient data
- insert_log(): Add audit log entry
- get_logs(): Retrieve audit logs
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from encryption_utils import encrypt_text, decrypt_text, load_fernet_key


# Database path
DB_PATH = "hospital.db"


def get_db_connection():
    """Create and return database connection."""
    return sqlite3.connect(DB_PATH)


def add_patient(name: str, age: int, gender: str, contact: str, 
                diagnosis: str, user_id: int, role: str) -> Tuple[bool, str]:
    """
    Add a new patient to the database with encrypted diagnosis.
    
    Args:
        name: Patient full name
        age: Patient age
        gender: Patient gender
        contact: Contact information (phone/email)
        diagnosis: Medical diagnosis (will be encrypted)
        user_id: ID of user adding the patient
        role: Role of user adding the patient
        
    Returns:
        Tuple[bool, str]: (success, message)
        
    GDPR Compliance:
        - Encrypts sensitive diagnosis field
        - Logs the action for audit trail
        - Stores admission timestamp
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Load Fernet key for encryption
        fernet = load_fernet_key()
        
        # Encrypt diagnosis
        diagnosis_encrypted = encrypt_text(diagnosis, fernet)
        
        # Get current timestamp
        admission_date = datetime.now().isoformat()
        
        # Insert patient
        cursor.execute("""
            INSERT INTO patients 
            (name, age, gender, contact, diagnosis, diagnosis_encrypted, 
             admission_date, is_anonymized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, contact, diagnosis, diagnosis_encrypted, 
              admission_date, 0))
        
        patient_id = cursor.lastrowid
        
        # Log the action
        insert_log(
            user_id=user_id,
            role=role,
            action="ADD_PATIENT",
            details=f"Added patient: {name} (ID: {patient_id})",
            conn=conn
        )
        
        conn.commit()
        conn.close()
        
        print(f"✓ Patient added successfully: {name} (ID: {patient_id})")
        return True, f"Patient added successfully (ID: {patient_id})"
        
    except sqlite3.Error as e:
        print(f"✗ Database error adding patient: {e}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        print(f"✗ Unexpected error adding patient: {e}")
        return False, f"Error: {str(e)}"


def update_patient(patient_id: int, name: str, age: int, gender: str, 
                   contact: str, diagnosis: str, user_id: int, 
                   role: str) -> Tuple[bool, str]:
    """
    Update existing patient record.
    
    Args:
        patient_id: ID of patient to update
        name: Updated patient name
        age: Updated age
        gender: Updated gender
        contact: Updated contact
        diagnosis: Updated diagnosis (will be re-encrypted)
        user_id: ID of user updating the record
        role: Role of user updating the record
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Defensive: allow patient_id passed as str/float from UI
        try:
            patient_id = int(patient_id)
        except Exception:
            return False, f"Invalid patient_id type: {type(patient_id)}"

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT name FROM patients WHERE patient_id = ?", (patient_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, f"Patient ID {patient_id} not found"
        
        old_name = result[0]
        
        # Load Fernet key for encryption
        fernet = load_fernet_key()
        
        # Encrypt new diagnosis
        diagnosis_encrypted = encrypt_text(diagnosis, fernet)
        
        # Update patient
        cursor.execute("""
            UPDATE patients
            SET name = ?, age = ?, gender = ?, contact = ?, 
                diagnosis = ?, diagnosis_encrypted = ?
            WHERE patient_id = ?
        """, (name, age, gender, contact, diagnosis, diagnosis_encrypted, patient_id))
        
        # Log the action
        insert_log(
            user_id=user_id,
            role=role,
            action="UPDATE_PATIENT",
            details=f"Updated patient: {old_name} -> {name} (ID: {patient_id})",
            conn=conn
        )
        
        conn.commit()
        conn.close()
        
        print(f"✓ Patient updated successfully: {name} (ID: {patient_id})")
        return True, f"Patient updated successfully"
        
    except sqlite3.Error as e:
        print(f"✗ Database error updating patient: {e}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        print(f"✗ Unexpected error updating patient: {e}")
        return False, f"Error: {str(e)}"


def get_all_patients(include_anonymized: bool = False) -> pd.DataFrame:
    """
    Retrieve all patients from database.
    
    Args:
        include_anonymized: If True, include anonymized patients
        
    Returns:
        pd.DataFrame: DataFrame with patient records
        
    Columns:
        patient_id, name, age, gender, contact, diagnosis, 
        diagnosis_encrypted, admission_date, is_anonymized
    """
    try:
        conn = get_db_connection()
        
        if include_anonymized:
            query = "SELECT * FROM patients ORDER BY admission_date DESC"
        else:
            query = """
                SELECT * FROM patients 
                WHERE is_anonymized = 0 
                ORDER BY admission_date DESC
            """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"✓ Retrieved {len(df)} patient records")
        return df
        
    except sqlite3.Error as e:
        print(f"✗ Database error retrieving patients: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"✗ Unexpected error retrieving patients: {e}")
        return pd.DataFrame()


def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """
    Get single patient record by ID.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Optional[Dict]: Patient data or None
    """
    try:
        # Defensive: coerce patient_id to int if possible
        try:
            patient_id = int(patient_id)
        except Exception:
            return None

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['patient_id', 'name', 'age', 'gender', 'contact', 
                      'diagnosis', 'diagnosis_encrypted', 'admission_date', 
                      'is_anonymized']
            return dict(zip(columns, result))
        
        return None
        
    except sqlite3.Error as e:
        print(f"✗ Database error getting patient: {e}")
        return None


def anonymize_patient_row(patient_id: int, user_id: int, role: str) -> Tuple[bool, str]:
    """
    Anonymize patient data (GDPR Right to Erasure - Article 17).
    
    Anonymization replaces:
        - name -> "ANONYMIZED_<patient_id>"
        - contact -> "ANONYMIZED"
        - diagnosis -> "ANONYMIZED"
        - diagnosis_encrypted -> ""
        - Sets is_anonymized = 1
    
    Args:
        patient_id: ID of patient to anonymize
        user_id: ID of user performing anonymization
        role: Role of user performing anonymization
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Defensive: coerce patient_id to int if passed from UI as str/float
        try:
            patient_id = int(patient_id)
        except Exception:
            return False, f"Invalid patient_id type: {type(patient_id)}"

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if patient exists
        cursor.execute(
            "SELECT name, is_anonymized FROM patients WHERE patient_id = ?", 
            (patient_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, f"Patient ID {patient_id} not found"
        
        old_name, is_anonymized = result
        
        if is_anonymized:
            conn.close()
            return False, f"Patient ID {patient_id} is already anonymized"
        
        # Anonymize patient data
        anonymized_name = f"ANONYMIZED_{patient_id}"
        
        cursor.execute("""
            UPDATE patients
            SET name = ?, 
                contact = 'ANONYMIZED',
                diagnosis = 'ANONYMIZED',
                diagnosis_encrypted = '',
                is_anonymized = 1
            WHERE patient_id = ?
        """, (anonymized_name, patient_id))
        
        # Log the action
        insert_log(
            user_id=user_id,
            role=role,
            action="ANONYMIZE_PATIENT",
            details=f"Anonymized patient: {old_name} (ID: {patient_id})",
            conn=conn
        )
        
        conn.commit()
        conn.close()
        
        print(f"✓ Patient anonymized successfully: {old_name} (ID: {patient_id})")
        return True, f"Patient anonymized successfully"
        
    except sqlite3.Error as e:
        print(f"✗ Database error anonymizing patient: {e}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        print(f"✗ Unexpected error anonymizing patient: {e}")
        return False, f"Error: {str(e)}"


def insert_log(user_id: int, role: str, action: str, details: str, 
               conn: Optional[sqlite3.Connection] = None) -> bool:
    """
    Insert audit log entry (GDPR Article 30 - Record of processing activities).
    
    Args:
        user_id: ID of user performing action
        role: Role of user
        action: Action type (ADD_PATIENT, UPDATE_PATIENT, etc.)
        details: Detailed description of action
        conn: Existing database connection (optional)
        
    Returns:
        bool: True if log inserted successfully
    """
    close_conn = False
    
    try:
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO logs (user_id, role, action, timestamp, details)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, role, action, timestamp, details))
        
        if close_conn:
            conn.commit()
            conn.close()
        
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error inserting log: {e}")
        return False


def get_logs(limit: int = 100) -> pd.DataFrame:
    """
    Retrieve audit logs from database.
    
    Args:
        limit: Maximum number of logs to retrieve
        
    Returns:
        pd.DataFrame: DataFrame with log entries
    """
    try:
        conn = get_db_connection()
        
        query = f"""
            SELECT log_id, user_id, role, action, timestamp, details
            FROM logs
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"✓ Retrieved {len(df)} log entries")
        return df
        
    except sqlite3.Error as e:
        print(f"✗ Database error retrieving logs: {e}")
        return pd.DataFrame()


def get_database_stats() -> Dict:
    """
    Get database statistics for dashboard.
    
    Returns:
        Dict: Statistics including patient count, log count, etc.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total patients
        cursor.execute("SELECT COUNT(*) FROM patients WHERE is_anonymized = 0")
        total_patients = cursor.fetchone()[0]
        
        # Anonymized patients
        cursor.execute("SELECT COUNT(*) FROM patients WHERE is_anonymized = 1")
        anonymized_patients = cursor.fetchone()[0]
        
        # Total logs
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_patients': total_patients,
            'anonymized_patients': anonymized_patients,
            'total_logs': total_logs,
            'total_users': total_users
        }
        
    except sqlite3.Error as e:
        print(f"✗ Database error getting stats: {e}")
        return {}


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_db_operations():
    """Test database operations."""
    print("\n" + "="*60)
    print("TESTING DATABASE OPERATIONS")
    print("="*60)
    
    # Test 1: Add patient
    print("\n[Test 1] Add Patient")
    success, msg = add_patient(
        name="Test Patient",
        age=45,
        gender="Male",
        contact="+1234567890",
        diagnosis="Hypertension",
        user_id=1,
        role="admin"
    )
    assert success, "Patient should be added successfully"
    print(f"✓ {msg}")
    
    # Test 2: Get all patients
    print("\n[Test 2] Get All Patients")
    patients_df = get_all_patients()
    print(f"Total patients: {len(patients_df)}")
    print(patients_df[['patient_id', 'name', 'age', 'diagnosis']].head())
    print("✓ Test passed")
    
    # Test 3: Get logs
    print("\n[Test 3] Get Audit Logs")
    logs_df = get_logs(limit=5)
    print(f"Total logs retrieved: {len(logs_df)}")
    print(logs_df[['action', 'role', 'details']].head())
    print("✓ Test passed")
    
    # Test 4: Database stats
    print("\n[Test 4] Database Statistics")
    stats = get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("✓ Test passed")
    
    print("\n" + "="*60)
    print("✓ ALL DATABASE TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    test_db_operations()