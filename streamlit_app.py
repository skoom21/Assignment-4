"""
streamlit_app.py
================
Main Streamlit UI for GDPR-Compliant Hospital Management System.

Features:
- Role-based access control (Admin, Doctor, Receptionist)
- Patient management with encryption
- Audit logging and visualization
- Data export (CSV)
- GDPR compliance (anonymization, right to erasure)

Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Import custom modules
from auth import (login_user, verify_session, init_session, login_session, 
                  logout_session, check_permission)
from db_helpers import (add_patient, update_patient, get_all_patients, 
                        anonymize_patient_row, get_logs, get_database_stats,
                        get_patient_by_id)
from encryption_utils import decrypt_text, mask_name, mask_contact, load_fernet_key
from graphs import (plot_actions_per_day, plot_actions_by_role, 
                    plot_actions_by_type, plot_hourly_activity,
                    plot_patient_age_distribution, plot_gender_distribution)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# SESSION INITIALIZATION
# ============================================================================

init_session(st.session_state)


# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #A23B72;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #E8F4F8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3CD;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F18F01;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D4EDDA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #06A77D;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# LOGIN PAGE
# ============================================================================

def show_login_page():
    """Display login page."""
    
    st.markdown('<div class="main-header">🏥 Hospital Management System</div>', 
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">GDPR-Compliant Patient Management</p>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="sub-header">🔐 Login</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", 
                                    placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    success, user_data = login_user(username, password)
                    
                    if success:
                        login_session(st.session_state, user_data)
                        st.success(f"✓ Welcome, {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("✗ Invalid username or password")
                else:
                    st.warning("⚠ Please enter both username and password")
        
        # Default credentials info
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**Default Login Credentials:**")
        st.markdown("- **Admin:** `admin` / `admin123`")
        st.markdown("- **Doctor:** `doctor1` / `doctor123`")
        st.markdown("- **Receptionist:** `receptionist1` / `recept123`")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

def show_admin_dashboard():
    """Display admin dashboard with full access."""
    
    user_data = st.session_state.user_data
    
    st.markdown(f'<div class="main-header">👨‍💼 Admin Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">Welcome, {user_data["username"]}</p>', 
                unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.markdown("### 📋 Navigation")
    page = st.sidebar.radio("Go to", [
        "📊 Dashboard Overview",
        "👥 Manage Patients",
        "📝 Add Patient",
        "🔒 Anonymize Patient",
        "📜 Audit Logs",
        "📈 Analytics",
        "💾 Export Data"
    ])
    
    if page == "📊 Dashboard Overview":
        show_dashboard_overview()
    elif page == "👥 Manage Patients":
        show_manage_patients_admin()
    elif page == "📝 Add Patient":
        show_add_patient_form()
    elif page == "🔒 Anonymize Patient":
        show_anonymize_patient()
    elif page == "📜 Audit Logs":
        show_audit_logs()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "💾 Export Data":
        show_export_data()


def show_dashboard_overview():
    """Display dashboard statistics."""
    
    st.markdown('<div class="sub-header">📊 System Overview</div>', unsafe_allow_html=True)
    
    # Get statistics
    stats = get_database_stats()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Active Patients", stats.get('total_patients', 0))
    
    with col2:
        st.metric("🔒 Anonymized", stats.get('anonymized_patients', 0))
    
    with col3:
        st.metric("📜 Audit Logs", stats.get('total_logs', 0))
    
    with col4:
        st.metric("👤 System Users", stats.get('total_users', 0))
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 🕐 Recent Activity")
    logs_df = get_logs(limit=10)
    
    if not logs_df.empty:
        display_df = logs_df[['timestamp', 'role', 'action', 'details']].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity")


def show_manage_patients_admin():
    """Admin view: Manage patients with decryption capability."""
    
    st.markdown('<div class="sub-header">👥 Patient Management (Admin View)</div>', 
                unsafe_allow_html=True)
    
    # Get all patients
    patients_df = get_all_patients(include_anonymized=False)
    
    if patients_df.empty:
        st.info("No patients in the database")
        return
    
    st.markdown(f"**Total Patients:** {len(patients_df)}")
    
    # View mode selection
    view_mode = st.radio("View Mode:", ["📋 Standard View", "🔓 Decrypted View"], horizontal=True)
    
    if view_mode == "📋 Standard View":
        # Standard view with masked data
        display_df = patients_df[['patient_id', 'name', 'age', 'gender', 
                                   'contact', 'admission_date']].copy()
        display_df['name'] = display_df['name'].apply(mask_name)
        display_df['contact'] = display_df['contact'].apply(mask_contact)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    else:
        # Decrypted view (Admin only)
        st.warning("⚠️ Viewing sensitive data with decryption privileges")
        
        fernet = load_fernet_key()
        display_df = patients_df[['patient_id', 'name', 'age', 'gender', 
                                   'contact', 'diagnosis', 'admission_date']].copy()
        
        # Decrypt diagnosis
        display_df['diagnosis_decrypted'] = patients_df['diagnosis_encrypted'].apply(
            lambda x: decrypt_text(x, fernet) if x else "N/A"
        )
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Edit patient section
    st.markdown("---")
    st.markdown("### ✏️ Edit Patient")
    
    patient_id = st.number_input("Enter Patient ID to Edit:", min_value=1, step=1)
    
    if st.button("Load Patient Data"):
        patient = get_patient_by_id(patient_id)
        
        if patient:
            st.session_state.edit_patient = patient
            st.success(f"✓ Loaded patient: {patient['name']}")
        else:
            st.error("✗ Patient not found")
    
    if 'edit_patient' in st.session_state:
        patient = st.session_state.edit_patient
        
        with st.form("edit_patient_form"):
            name = st.text_input("Name", value=patient['name'])
            age = st.number_input("Age", value=patient['age'], min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                 index=["Male", "Female", "Other"].index(patient['gender']))
            contact = st.text_input("Contact", value=patient['contact'])
            diagnosis = st.text_area("Diagnosis", value=patient['diagnosis'])
            
            submit = st.form_submit_button("Update Patient")
            
            if submit:
                success, msg = update_patient(
                    patient_id=patient['patient_id'],
                    name=name,
                    age=age,
                    gender=gender,
                    contact=contact,
                    diagnosis=diagnosis,
                    user_id=st.session_state.user_data['user_id'],
                    role=st.session_state.user_data['role']
                )
                
                if success:
                    st.success(msg)
                    del st.session_state.edit_patient
                    st.rerun()
                else:
                    st.error(msg)


def show_add_patient_form():
    """Form to add new patient."""
    
    st.markdown('<div class="sub-header">📝 Add New Patient</div>', unsafe_allow_html=True)
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Patient Name*", placeholder="John Doe")
            age = st.number_input("Age*", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
        
        with col2:
            contact = st.text_input("Contact*", placeholder="+1234567890 or email@example.com")
            diagnosis = st.text_area("Diagnosis*", placeholder="Enter medical diagnosis")
        
        submit = st.form_submit_button("Add Patient", use_container_width=True)
        
        if submit:
            if name and contact and diagnosis:
                success, msg = add_patient(
                    name=name,
                    age=age,
                    gender=gender,
                    contact=contact,
                    diagnosis=diagnosis,
                    user_id=st.session_state.user_data['user_id'],
                    role=st.session_state.user_data['role']
                )
                
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("⚠ Please fill all required fields")


def show_anonymize_patient():
    """GDPR Right to Erasure: Anonymize patient data."""
    
    st.markdown('<div class="sub-header">🔒 Anonymize Patient Data</div>', 
                unsafe_allow_html=True)
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("**⚠️ GDPR Article 17: Right to Erasure**")
    st.markdown("This action will permanently anonymize patient data. This cannot be undone.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show non-anonymized patients
    patients_df = get_all_patients(include_anonymized=False)
    
    if patients_df.empty:
        st.info("No patients available to anonymize")
        return
    
    st.markdown("### Available Patients")
    display_df = patients_df[['patient_id', 'name', 'age', 'admission_date']].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Anonymization form
    st.markdown("---")
    patient_id = st.number_input("Enter Patient ID to Anonymize:", min_value=1, step=1)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Anonymize Patient", type="primary"):
            success, msg = anonymize_patient_row(
                patient_id=patient_id,
                user_id=st.session_state.user_data['user_id'],
                role=st.session_state.user_data['role']
            )
            
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def show_audit_logs():
    """Display audit logs."""
    
    st.markdown('<div class="sub-header">📜 Audit Logs</div>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        limit = st.slider("Number of logs to display:", 10, 500, 100)
    
    with col2:
        action_filter = st.multiselect("Filter by Action:", 
                                       ["ADD_PATIENT", "UPDATE_PATIENT", 
                                        "ANONYMIZE_PATIENT", "VIEW_LOGS", 
                                        "LOGIN", "LOGOUT"])
    
    # Get logs
    logs_df = get_logs(limit=limit)
    
    # Apply filters
    if action_filter:
        logs_df = logs_df[logs_df['action'].isin(action_filter)]
    
    if not logs_df.empty:
        st.markdown(f"**Showing {len(logs_df)} log entries**")
        
        display_df = logs_df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No logs found")


def show_analytics():
    """Display analytics and visualizations."""
    
    st.markdown('<div class="sub-header">📈 Analytics & Visualizations</div>', 
                unsafe_allow_html=True)
    
    logs_df = get_logs(limit=500)
    patients_df = get_all_patients(include_anonymized=False)
    
    if logs_df.empty:
        st.info("No data available for analytics")
        return
    
    # Activity Timeline
    st.markdown("### 📅 Activity Timeline")
    fig = plot_actions_per_day(logs_df)
    if fig:
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Actions by Role")
        fig = plot_actions_by_role(logs_df)
        if fig:
            st.pyplot(fig)
    
    with col2:
        st.markdown("### 📊 Actions by Type")
        fig = plot_actions_by_type(logs_df)
        if fig:
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Hourly activity
    st.markdown("### 🕐 Hourly Activity Pattern")
    fig = plot_hourly_activity(logs_df)
    if fig:
        st.pyplot(fig)
    
    # Patient analytics
    if not patients_df.empty:
        st.markdown("---")
        st.markdown("### 👥 Patient Demographics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = plot_patient_age_distribution(patients_df)
            if fig:
                st.pyplot(fig)
        
        with col2:
            fig = plot_gender_distribution(patients_df)
            if fig:
                st.pyplot(fig)


def show_export_data():
    """Export data to CSV."""
    
    st.markdown('<div class="sub-header">💾 Export Data</div>', unsafe_allow_html=True)
    
    st.markdown("Export patient data and audit logs to CSV files for backup and compliance.")
    
    # Export patients
    st.markdown("### 👥 Export Patients")
    
    if st.button("Export Patients to CSV"):
        patients_df = get_all_patients(include_anonymized=True)
        
        if not patients_df.empty:
            csv = patients_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Patients CSV",
                data=csv,
                file_name=f"patients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success(f"✓ Exported {len(patients_df)} patient records")
        else:
            st.info("No patient data to export")
    
    st.markdown("---")
    
    # Export logs
    st.markdown("### 📜 Export Audit Logs")
    
    if st.button("Export Logs to CSV"):
        logs_df = get_logs(limit=10000)
        
        if not logs_df.empty:
            csv = logs_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Logs CSV",
                data=csv,
                file_name=f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success(f"✓ Exported {len(logs_df)} log entries")
        else:
            st.info("No log data to export")


# ============================================================================
# DOCTOR DASHBOARD
# ============================================================================

def show_doctor_dashboard():
    """Display doctor dashboard with anonymized view only."""
    
    user_data = st.session_state.user_data
    
    st.markdown(f'<div class="main-header">👨‍⚕️ Doctor Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">Welcome, Dr. {user_data["username"]}</p>', 
                unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("**🔒 Privacy Notice:** You are viewing anonymized patient data in compliance with GDPR.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get patients
    patients_df = get_all_patients(include_anonymized=False)
    
    if patients_df.empty:
        st.info("No patients in the database")
        return
    
    st.markdown(f"### 👥 Patient List ({len(patients_df)} patients)")
    
    # Display anonymized data
    display_df = patients_df[['patient_id', 'name', 'age', 'gender', 
                               'contact', 'admission_date']].copy()
    
    # Mask sensitive fields
    display_df['name'] = display_df['name'].apply(mask_name)
    display_df['contact'] = display_df['contact'].apply(mask_contact)
    display_df['diagnosis'] = "🔒 ENCRYPTED"
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("**Note:** Diagnosis fields are encrypted. Contact admin for access to sensitive medical information.")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# RECEPTIONIST DASHBOARD
# ============================================================================

def show_receptionist_dashboard():
    """Display receptionist dashboard."""
    
    user_data = st.session_state.user_data
    
    st.markdown(f'<div class="main-header">📋 Receptionist Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">Welcome, {user_data["username"]}</p>', 
                unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.markdown("### 📋 Navigation")
    page = st.sidebar.radio("Go to", [
        "👥 View Patients",
        "📝 Add Patient",
        "✏️ Edit Patient"
    ])
    
    if page == "👥 View Patients":
        show_patients_receptionist()
    elif page == "📝 Add Patient":
        show_add_patient_form()
    elif page == "✏️ Edit Patient":
        show_edit_patient_receptionist()


def show_patients_receptionist():
    """Receptionist view: Basic patient info only."""
    
    st.markdown("### 👥 Patient List")
    
    patients_df = get_all_patients(include_anonymized=False)
    
    if patients_df.empty:
        st.info("No patients in the database")
        return
    
    # Limited view - no diagnosis
    display_df = patients_df[['patient_id', 'name', 'age', 'gender', 
                               'contact', 'admission_date']].copy()
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.info("🔒 Diagnosis information is restricted. Contact admin for medical details.")


def show_edit_patient_receptionist():
    """Receptionist edit patient (no diagnosis access)."""
    
    st.markdown("### ✏️ Edit Patient")
    
    patient_id = st.number_input("Enter Patient ID to Edit:", min_value=1, step=1)
    
    if st.button("Load Patient Data"):
        patient = get_patient_by_id(patient_id)
        
        if patient:
            st.session_state.edit_patient = patient
            st.success(f"✓ Loaded patient: {patient['name']}")
        else:
            st.error("✗ Patient not found")
    
    if 'edit_patient' in st.session_state:
        patient = st.session_state.edit_patient
        
        with st.form("edit_patient_receptionist"):
            name = st.text_input("Name", value=patient['name'])
            age = st.number_input("Age", value=patient['age'], min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                 index=["Male", "Female", "Other"].index(patient['gender']))
            contact = st.text_input("Contact", value=patient['contact'])
            
            st.info("🔒 Diagnosis field is restricted for receptionists")
            
            submit = st.form_submit_button("Update Patient")
            
            if submit:
                # Keep existing diagnosis
                success, msg = update_patient(
                    patient_id=patient['patient_id'],
                    name=name,
                    age=age,
                    gender=gender,
                    contact=contact,
                    diagnosis=patient['diagnosis'],  # Keep original
                    user_id=st.session_state.user_data['user_id'],
                    role=st.session_state.user_data['role']
                )
                
                if success:
                    st.success(msg)
                    del st.session_state.edit_patient
                    st.rerun()
                else:
                    st.error(msg)


# ============================================================================
# MAIN APP LOGIC
# ============================================================================

def main():
    """Main application logic."""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏥 Hospital System")
        st.markdown("---")
        
        if verify_session(st.session_state):
            user_data = st.session_state.user_data
            st.markdown(f"**User:** {user_data['username']}")
            st.markdown(f"**Role:** {user_data['role'].upper()}")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_session(st.session_state)
                st.rerun()
        else:
            st.info("Please login to continue")
    
    # Route to appropriate page
    if not verify_session(st.session_state):
        show_login_page()
    else:
        user_role = st.session_state.user_data['role'].lower()
        
        if user_role == 'admin':
            show_admin_dashboard()
        elif user_role == 'doctor':
            show_doctor_dashboard()
        elif user_role == 'receptionist':
            show_receptionist_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown('<div class="footer">🔒 GDPR-Compliant Hospital Management System | Built with Streamlit</div>', 
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()