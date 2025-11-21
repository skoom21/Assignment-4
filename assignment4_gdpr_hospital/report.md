# Assignment 4 — GDPR-Compliant Mini Hospital Management System

## 1. Introduction
Brief: This project demonstrates a small-scale hospital management dashboard implementing key privacy principles and the CIA triad in compliance with GDPR.

## 2. System Overview
- Stack: Streamlit (frontend), SQLite (database), Python utilities
- CIA mapping:
  - Confidentiality: deterministic anonymization (SHA256-derived ANON_), masking of contact, RBAC (admin/doctor/receptionist)
  - Integrity: activity logs (who/when/what), DB constraints, admin audit view
  - Availability: CSV export, timestamped DB, try/except error handling

[Insert system overview diagram here — show user/auth layer, anonymization layer, DB, logging/audit, and admin console]

## 3. Implementation Details
- Authentication: basic username/password stored as SHA256 (explain: in production use salted hashing e.g., bcrypt)
- Anonymization: non-reversible hashing for names; masked contact numbers
- Logging: logs table storing user_id, role, action, timestamp, details
- RBAC: enforced in Streamlit UI and server-side checks before DB writes/reads

## 4. GDPR Alignment
- Lawful basis: purpose-limited processing for healthcare
- Data minimisation: anonymization when possible
- Access control: role-based view restriction
- Auditability: logs and export for accountability
- Retention & rights: (optional) implement deletion/timer and consent banner to fully comply

## 5. Screenshots
- Login screen
- Anonymization action
- Audit log

## 6. Conclusion
Short reflection on limitations and potential improvements: use bcrypt, HTTPS, real auth provider, per-field encryption with KMS, retention policy, consent management.
