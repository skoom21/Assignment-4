import sqlite3
import os
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime

DB_NAME = "hospital.db"
KEY_FILE = "fernet.key"

# -------------------------------------------------------
# Generate Fernet encryption key (only once)
# -------------------------------------------------------
def generate_fernet_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("✔ Generated new Fernet key (fernet.key)")
    else:
        print("✔ Fernet key already exists — not overwritten")

def load_fernet_key():
    """Load Fernet key from file."""
    with open(KEY_FILE, "rb") as f:
        return Fernet(f.read())

def encrypt_text(text, fernet):
    """Encrypt text using Fernet."""
    if text:
        return fernet.encrypt(text.encode()).decode()
    return ""


# -------------------------------------------------------
# Initialize SQLite Database
# -------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # -----------------------------
    # USERS TABLE
    # -----------------------------
    # Create users table with password_hash and created_at. If an older schema exists
    # with a `password` column, migrate passwords by hashing the existing value.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cur.fetchone():
        # Table exists — check columns
        cur.execute("PRAGMA table_info(users);")
        cols = [r[1] for r in cur.fetchall()]
        if 'password_hash' not in cols:
            print("⚠ users table missing 'password_hash' column — migrating table...")
            # Rename old table and create new one
            cur.execute("ALTER TABLE users RENAME TO users_old;")
            cur.execute(
                """
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            # If old password column exists, copy username/role and hash passwords
            cur.execute("PRAGMA table_info(users_old);")
            old_cols = [r[1] for r in cur.fetchall()]
            if 'password' in old_cols:
                cur.execute("SELECT username, password, role FROM users_old;")
                rows = cur.fetchall()
                for username, password, role in rows:
                    pwd_hash = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
                    cur.execute(
                        "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                        (username, pwd_hash, role, datetime.now().isoformat()),
                    )
                print(f"✔ Migrated {len(rows)} users from old schema")
            else:
                print("ℹ users_old table found but no 'password' column — creating empty users table")
            # Drop old table
            cur.execute("DROP TABLE IF EXISTS users_old;")
        else:
            # users table already has password_hash column — nothing to do
            pass
    else:
        # Create a fresh users table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    # Insert RBAC default users if no users exist
    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        def _hash(p):
            return hashlib.sha256(p.encode('utf-8')).hexdigest()

        default_users = [
            ("admin", _hash("admin123"), "admin"),
            ("doctor1", _hash("doctor123"), "doctor"),
            ("receptionist1", _hash("recept123"), "receptionist"),
        ]
        cur.executemany(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            [(u, ph, r, datetime.now().isoformat()) for (u, ph, r) in default_users],
        )
        print("✔ Inserted default RBAC users (hashed passwords)")

    # -----------------------------
    # PATIENTS TABLE
    # -----------------------------
    # Drop and recreate to update schema
    cur.execute("DROP TABLE IF EXISTS patients;")
    cur.execute(
        """
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            diagnosis TEXT,
            diagnosis_encrypted TEXT,
            admission_date TEXT DEFAULT CURRENT_TIMESTAMP,
            is_anonymized INTEGER DEFAULT 0
        );
        """
    )

    # Insert sample patients if none exist
    cur.execute("SELECT COUNT(*) FROM patients;")
    if cur.fetchone()[0] == 0:
        fernet = load_fernet_key()
        sample_patients = [
            ("John Doe", 45, "Male", "+1234567890", "Hypertension"),
            ("Jane Smith", 32, "Female", "jane@email.com", "Asthma"),
            ("Bob Johnson", 67, "Male", "+1987654321", "Diabetes Type 2"),
            ("Alice Brown", 28, "Female", "alice@email.com", "Migraine"),
            ("Charlie Wilson", 52, "Male", "+1555123456", "Coronary Artery Disease"),
            ("Diana Davis", 41, "Female", "diana@email.com", "Thyroid Disorder"),
            ("Edward Miller", 73, "Male", "+1444987654", "Osteoarthritis"),
            ("Fiona Garcia", 36, "Female", "fiona@email.com", "Depression"),
            ("George Lee", 59, "Male", "+1333876543", "Chronic Kidney Disease"),
            ("Helen Taylor", 24, "Female", "helen@email.com", "Anxiety Disorder"),
            ("Ian Anderson", 38, "Male", "+1222765432", "Back Pain"),
            ("Julia Martinez", 55, "Female", "julia@email.com", "High Cholesterol"),
            ("Kevin White", 49, "Male", "+1111654321", "GERD"),
            ("Laura Thompson", 31, "Female", "laura@email.com", "Allergies"),
            ("Michael Harris", 64, "Male", "+1000543210", "Prostate Issues"),
            ("Nancy Clark", 27, "Female", "nancy@email.com", "Insomnia"),
            ("Oliver Lewis", 43, "Male", "+1999432109", "Arthritis"),
            ("Paula Walker", 39, "Female", "paula@email.com", "Fibromyalgia"),
            ("Quincy Hall", 71, "Male", "+1888321098", "COPD"),
            ("Rachel Young", 33, "Female", "rachel@email.com", "Endometriosis"),
            ("Samuel King", 58, "Male", "+1777210987", "Sleep Apnea"),
            ("Tina Wright", 46, "Female", "tina@email.com", "Irritable Bowel Syndrome"),
            ("Ulysses Adams", 62, "Male", "+1666109876", "Parkinson's Disease"),
            ("Victoria Nelson", 29, "Female", "victoria@email.com", "PCOS"),
            ("William Carter", 54, "Male", "+1555098765", "Hepatitis C"),
        ]
        for name, age, gender, contact, diagnosis in sample_patients:
            encrypted_diag = encrypt_text(diagnosis, fernet)
            cur.execute(
                "INSERT INTO patients (name, age, gender, contact, diagnosis, diagnosis_encrypted) VALUES (?, ?, ?, ?, ?, ?)",
                (name, age, gender, contact, diagnosis, encrypted_diag)
            )
        print("✔ Inserted 25 sample patients")

    # -----------------------------
    # LOGS TABLE
    # -----------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )

    conn.commit()
    conn.close()
    print(f"✔ Database initialized: {DB_NAME}")


# -------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------
if __name__ == "__main__":
    generate_fernet_key()
    init_db()
    print("✔ All setup complete.")