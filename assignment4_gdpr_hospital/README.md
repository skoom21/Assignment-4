# 🏥 GDPR-Compliant Hospital Management System

A privacy-centric hospital management system built with **Python**, **Streamlit**, and **SQLite**, following GDPR compliance principles.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [GDPR Compliance](#gdpr-compliance)
- [Security Features](#security-features)
- [File Structure](#file-structure)
- [Testing](#testing)
- [Screenshots](#screenshots)

---

## ✨ Features

### 🔐 Security & Privacy
- **Fernet Symmetric Encryption** for sensitive diagnosis data
- **SHA-256 Password Hashing** for user authentication
- **Role-Based Access Control (RBAC)** with 3 roles:
  - 👨‍💼 **Admin**: Full access (decrypt, anonymize, logs)
  - 👨‍⚕️ **Doctor**: View anonymized patient data only
  - 📋 **Receptionist**: Add/edit patients (no diagnosis access)

### 📊 Patient Management
- Add, edit, and view patient records
- Encrypted storage of medical diagnoses
- Patient anonymization (GDPR Right to Erasure)
- Age and gender demographics

### 📜 Audit Trail
- Comprehensive logging of all system actions
- Timestamp and user tracking
- Action type categorization
- Exportable audit logs

### 📈 Analytics & Visualization
- Activity timeline charts
- Role-based action distribution
- Hourly activity patterns
- Patient age distribution
- Gender demographics pie charts

### 💾 Data Export
- CSV export for patients
- CSV export for audit logs
- GDPR-compliant data portability

---

## 🏗️ Architecture

### CIA Triad Implementation

| Principle | Implementation |
|-----------|---------------|
| **Confidentiality** | Fernet encryption, role-based access, data masking |
| **Integrity** | Audit logging, transaction management, input validation |
| **Availability** | Error handling, database backups, CSV exports |

### Database Schema

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ user_id (PK)    │
│ username        │
│ password_hash   │
│ role            │
│ created_at      │
└─────────────────┘

┌─────────────────────────┐
│       PATIENTS          │
├─────────────────────────┤
│ patient_id (PK)         │
│ name                    │
│ age                     │
│ gender                  │
│ contact                 │
│ diagnosis               │
│ diagnosis_encrypted     │
│ admission_date          │
│ is_anonymized           │
└─────────────────────────┘

┌─────────────────┐
│      LOGS       │
├─────────────────┤
│ log_id (PK)     │
│ user_id (FK)    │
│ role            │
│ action          │
│ timestamp       │
│ details         │
└─────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download Project

```bash
# Create project directory
mkdir hospital_management
cd hospital_management
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `matplotlib` - Data visualization
- `cryptography` - Fernet encryption

### Step 3: Initialize Database

```bash
python db_init.py
```

This creates:
- `hospital.db` - SQLite database
- `fernet.key` - Encryption key
- Default user accounts
- Database schema

**When prompted**, enter `y` to add sample patients for testing.

---

## 💻 Usage

### Starting the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `doctor1` | `doctor123` |
| Receptionist | `receptionist1` | `recept123` |

---

## 🔒 GDPR Compliance

This system implements key GDPR principles:

### Article 5 - Data Processing Principles
✅ **Lawfulness, Fairness, Transparency**: Clear role-based access  
✅ **Purpose Limitation**: Data collected for patient care only  
✅ **Data Minimization**: Only essential data stored  
✅ **Accuracy**: Edit functionality maintains data accuracy  
✅ **Storage Limitation**: Anonymization removes identifiable data  
✅ **Integrity & Confidentiality**: Encryption and access controls

### Article 17 - Right to Erasure
✅ Patient anonymization feature removes all identifiable information

### Article 30 - Record of Processing Activities
✅ Comprehensive audit log tracks all data access and modifications

### Article 32 - Security of Processing
✅ Encryption at rest (Fernet)  
✅ Password hashing (SHA-256)  
✅ Role-based access control  
✅ Audit trail for accountability

---

## 🛡️ Security Features

### 1. Encryption
```python
# Fernet symmetric encryption (AES-128)
diagnosis_encrypted = encrypt_text("Hypertension")
diagnosis_decrypted = decrypt_text(encrypted_text)
```

### 2. Data Masking
```python
# Name masking: "John Doe" → "J**n D*e"
masked = mask_name("John Doe")

# Contact masking: "+1234567890" → "+12****7890"
masked = mask_contact("+1234567890")
```

### 3. Role-Based Access

| Feature | Admin | Doctor | Receptionist |
|---------|-------|--------|--------------|
| View Patients | ✅ Full | ✅ Masked | ✅ Basic |
| Decrypt Diagnosis | ✅ | ❌ | ❌ |
| Add Patient | ✅ | ❌ | ✅ |
| Edit Patient | ✅ | ❌ | ✅ (Limited) |
| Anonymize Patient | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ |
| Export Data | ✅ | ❌ | ❌ |

---

## 📁 File Structure

```
hospital_management/
│
├── db_init.py              # Database initialization
├── encryption_utils.py     # Encryption/decryption functions
├── auth.py                 # Authentication & RBAC
├── db_helpers.py           # Database CRUD operations
├── graphs.py               # Data visualization
├── streamlit_app.py        # Main UI application
│
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
│
├── hospital.db            # SQLite database (auto-generated)
└── fernet.key             # Encryption key (auto-generated)
```

---

## 🧪 Testing

### Test Individual Modules

```bash
# Test encryption
python encryption_utils.py

# Test authentication
python auth.py

# Test database operations
python db_helpers.py

# Test graph generation
python graphs.py
```

### Test Complete Workflow

1. **Initialize Database**
   ```bash
   python db_init.py
   ```

2. **Start Application**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Login as Admin**
   - Username: `admin`
   - Password: `admin123`

4. **Add Patient**
   - Navigate to "📝 Add Patient"
   - Fill form and submit

5. **View Encrypted Data**
   - Navigate to "👥 Manage Patients"
   - Switch to "🔓 Decrypted View"

6. **Test Anonymization**
   - Navigate to "🔒 Anonymize Patient"
   - Enter patient ID and confirm

7. **View Audit Logs**
   - Navigate to "📜 Audit Logs"
   - Filter by action type

8. **Generate Analytics**
   - Navigate to "📈 Analytics"
   - View all graphs

9. **Export Data**
   - Navigate to "💾 Export Data"
   - Download CSV files

---

## 📸 Screenshots

### Login Page
```
🏥 Hospital Management System
GDPR-Compliant Patient Management

🔐 Login
[Username: ________]
[Password: ________]
[Login Button]
```

### Admin Dashboard
```
👨‍💼 Admin Dashboard

📊 Dashboard Overview
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 👥 Active    │ 🔒 Anonymized│ 📜 Audit     │ 👤 System    │
│ Patients: 5  │ Patients: 2  │ Logs: 47     │ Users: 5     │
└──────────────┴──────────────┴──────────────┴──────────────┘

🕐 Recent Activity
[Timestamp]    [Role]    [Action]    [Details]
...
```

### Doctor Dashboard (Anonymized View)
```
👨‍⚕️ Doctor Dashboard

🔒 Privacy Notice: Viewing anonymized patient data

👥 Patient List (5 patients)
┌────┬──────────┬─────┬────────┬─────────┬──────────────┐
│ ID │ Name     │ Age │ Gender │ Contact │ Diagnosis    │
├────┼──────────┼─────┼────────┼─────────┼──────────────┤
│ 1  │ J*** S***│ 45  │ Male   │ +12**** │ 🔒 ENCRYPTED │
└────┴──────────┴─────┴────────┴─────────┴──────────────┘
```

---

## 🎯 Key Workflows

### Workflow 1: Adding a Patient (Receptionist)
1. Login as receptionist
2. Navigate to "📝 Add Patient"
3. Fill patient details
4. Submit form
5. ✅ Patient encrypted and logged

### Workflow 2: Viewing Sensitive Data (Admin)
1. Login as admin
2. Navigate to "👥 Manage Patients"
3. Select "🔓 Decrypted View"
4. View decrypted diagnoses
5. ✅ Access logged in audit trail

### Workflow 3: Anonymizing Patient (GDPR)
1. Login as admin
2. Navigate to "🔒 Anonymize Patient"
3. Enter patient ID
4. Confirm anonymization
5. ✅ Patient data permanently anonymized

---

## ⚠️ Important Notes

### Security Warnings

1. **Encryption Key Protection**
   - `fernet.key` file contains encryption key
   - In production: Use AWS KMS, Azure Key Vault, or similar
   - Never commit `fernet.key` to version control

2. **Password Security**
   - Default passwords are for testing only
   - Change all default passwords in production
   - Use bcrypt or argon2 for production password hashing

3. **Database Security**
   - `hospital.db` contains all patient data
   - Implement regular backups
   - Secure file permissions on server

### Production Deployment Checklist

- [ ] Change all default passwords
- [ ] Use secure key management (KMS)
- [ ] Implement HTTPS/TLS
- [ ] Add rate limiting
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Implement 2FA for admin accounts
- [ ] Add input sanitization
- [ ] Enable SQL injection protection
- [ ] Implement session timeout
- [ ] Add CAPTCHA for login
- [ ] Set secure cookie flags

---

## 📚 Additional Resources

### GDPR References
- [GDPR Official Text](https://gdpr.eu/)
- [Article 17 - Right to Erasure](https://gdpr.eu/article-17-right-to-be-forgotten/)
- [Article 30 - Record of Processing](https://gdpr.eu/article-30-record-of-processing-activities/)
- [Article 32 - Security of Processing](https://gdpr.eu/article-32-security-of-processing/)

### Technology Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Cryptography Library](https://cryptography.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 👥 Support

For issues or questions:
1. Check this README
2. Review code comments
3. Test individual modules
4. Check Streamlit logs

---

## 📄 License

This project is for educational purposes demonstrating GDPR-compliant system design.

---

## ✅ Completion Checklist

- [x] Database schema implemented
- [x] Encryption system working
- [x] Authentication with RBAC
- [x] Patient CRUD operations
- [x] Anonymization feature
- [x] Audit logging
- [x] Data visualization
- [x] CSV export functionality
- [x] Complete documentation
- [x] Testing procedures

---

**🎉 System Ready for Use!**

Run: `streamlit run streamlit_app.py`