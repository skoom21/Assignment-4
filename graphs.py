"""
graphs.py
=========
Data visualization functions for GDPR Hospital Management System.
Generates matplotlib figures for audit log analysis and activity monitoring.

Functions:
- plot_actions_per_day(): Activity timeline
- plot_actions_by_role(): Role distribution
- plot_actions_by_type(): Action type distribution
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import Optional


def plot_actions_per_day(logs_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a timeline plot showing actions per day.
    
    Args:
        logs_df: DataFrame with columns ['timestamp', 'action']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
        
    Example:
        >>> logs_df = get_logs()
        >>> fig = plot_actions_per_day(logs_df)
        >>> st.pyplot(fig)
    """
    try:
        if logs_df.empty:
            print("⚠ No logs to plot")
            return None
        
        # Convert timestamp to datetime
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df['date'] = logs_df['timestamp'].dt.date
        
        # Count actions per day
        actions_per_day = logs_df.groupby('date').size().reset_index(name='count')
        actions_per_day['date'] = pd.to_datetime(actions_per_day['date'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 5))
        
        ax.plot(actions_per_day['date'], actions_per_day['count'], 
                marker='o', linewidth=2, markersize=8, color='#2E86AB')
        
        ax.fill_between(actions_per_day['date'], actions_per_day['count'], 
                        alpha=0.3, color='#2E86AB')
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Actions', fontsize=12, fontweight='bold')
        ax.set_title('System Activity Timeline', fontsize=14, fontweight='bold', pad=20)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        print(f"✓ Generated actions per day plot ({len(actions_per_day)} days)")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating actions per day plot: {e}")
        return None


def plot_actions_by_role(logs_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a bar chart showing action distribution by role.
    
    Args:
        logs_df: DataFrame with columns ['role', 'action']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
    """
    try:
        if logs_df.empty:
            print("⚠ No logs to plot")
            return None
        
        # Count actions by role
        role_counts = logs_df['role'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#A23B72', '#F18F01', '#2E86AB']
        bars = ax.bar(role_counts.index, role_counts.values, color=colors[:len(role_counts)])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Formatting
        ax.set_xlabel('Role', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Actions', fontsize=12, fontweight='bold')
        ax.set_title('Actions by User Role', fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax.set_axisbelow(True)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        print(f"✓ Generated actions by role plot")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating actions by role plot: {e}")
        return None


def plot_actions_by_type(logs_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a horizontal bar chart showing action type distribution.
    
    Args:
        logs_df: DataFrame with columns ['action']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
    """
    try:
        if logs_df.empty:
            print("⚠ No logs to plot")
            return None
        
        # Count actions by type
        action_counts = logs_df['action'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = plt.cm.viridis(range(len(action_counts)))
        bars = ax.barh(action_counts.index, action_counts.values, color=colors)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, action_counts.values)):
            ax.text(value + 0.5, i, f'{int(value)}',
                   va='center', fontsize=10, fontweight='bold')
        
        # Formatting
        ax.set_xlabel('Count', fontsize=12, fontweight='bold')
        ax.set_ylabel('Action Type', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of Action Types', fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        ax.set_axisbelow(True)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        print(f"✓ Generated actions by type plot")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating actions by type plot: {e}")
        return None


def plot_hourly_activity(logs_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a plot showing activity by hour of day.
    
    Args:
        logs_df: DataFrame with columns ['timestamp']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
    """
    try:
        if logs_df.empty:
            print("⚠ No logs to plot")
            return None
        
        # Convert timestamp and extract hour
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        logs_df['hour'] = logs_df['timestamp'].dt.hour
        
        # Count actions by hour
        hourly_counts = logs_df['hour'].value_counts().sort_index()
        
        # Ensure all 24 hours are represented
        all_hours = pd.Series(0, index=range(24))
        all_hours.update(hourly_counts)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 5))
        
        ax.bar(all_hours.index, all_hours.values, color='#06A77D', alpha=0.7, edgecolor='black')
        
        # Formatting
        ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Actions', fontsize=12, fontweight='bold')
        ax.set_title('Activity by Hour of Day', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(0, 24, 2))
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax.set_axisbelow(True)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        print(f"✓ Generated hourly activity plot")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating hourly activity plot: {e}")
        return None


def plot_patient_age_distribution(patients_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a histogram showing patient age distribution.
    
    Args:
        patients_df: DataFrame with columns ['age']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
    """
    try:
        if patients_df.empty:
            print("⚠ No patient data to plot")
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(patients_df['age'], bins=20, color='#F18F01', alpha=0.7, 
                edgecolor='black', linewidth=1.2)
        
        # Add mean line
        mean_age = patients_df['age'].mean()
        ax.axvline(mean_age, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean Age: {mean_age:.1f}')
        
        # Formatting
        ax.set_xlabel('Age', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Patients', fontsize=12, fontweight='bold')
        ax.set_title('Patient Age Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.legend()
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax.set_axisbelow(True)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        print(f"✓ Generated patient age distribution plot")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating age distribution plot: {e}")
        return None


def plot_gender_distribution(patients_df: pd.DataFrame) -> Optional[plt.Figure]:
    """
    Create a pie chart showing patient gender distribution.
    
    Args:
        patients_df: DataFrame with columns ['gender']
        
    Returns:
        matplotlib.figure.Figure: Figure object or None if error
    """
    try:
        if patients_df.empty:
            print("⚠ No patient data to plot")
            return None
        
        # Count by gender
        gender_counts = patients_df['gender'].value_counts()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D']
        
        wedges, texts, autotexts = ax.pie(
            gender_counts.values, 
            labels=gender_counts.index,
            autopct='%1.1f%%',
            colors=colors[:len(gender_counts)],
            startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        
        # Make percentage text white and bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(14)
        
        ax.set_title('Patient Gender Distribution', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        print(f"✓ Generated gender distribution plot")
        return fig
        
    except Exception as e:
        print(f"✗ Error creating gender distribution plot: {e}")
        return None


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_graphs():
    """Test graph generation with sample data."""
    print("\n" + "="*60)
    print("TESTING GRAPH GENERATION")
    print("="*60)
    
    # Create sample logs data
    print("\n[Test 1] Creating sample data...")
    sample_logs = pd.DataFrame({
        'timestamp': pd.date_range(start='2025-01-01', periods=50, freq='H'),
        'action': ['ADD_PATIENT', 'UPDATE_PATIENT', 'VIEW_LOGS', 'ANONYMIZE_PATIENT'] * 12 + ['LOGIN', 'LOGOUT'],
        'role': ['admin', 'doctor', 'receptionist'] * 16 + ['admin', 'doctor']
    })
    
    sample_patients = pd.DataFrame({
        'age': [25, 35, 45, 55, 65, 30, 40, 50, 60, 70],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female']
    })
    
    print(f"✓ Created {len(sample_logs)} log entries and {len(sample_patients)} patient records")
    
    # Test each graph
    print("\n[Test 2] Testing graph functions...")
    
    graphs_to_test = [
        ("Actions per Day", plot_actions_per_day, sample_logs),
        ("Actions by Role", plot_actions_by_role, sample_logs),
        ("Actions by Type", plot_actions_by_type, sample_logs),
        ("Hourly Activity", plot_hourly_activity, sample_logs),
        ("Age Distribution", plot_patient_age_distribution, sample_patients),
        ("Gender Distribution", plot_gender_distribution, sample_patients)
    ]
    
    for name, func, data in graphs_to_test:
        print(f"\n  Testing: {name}")
        fig = func(data)
        if fig:
            print(f"  ✓ {name} generated successfully")
            plt.close(fig)  # Close to avoid memory issues
        else:
            print(f"  ✗ {name} failed")
    
    print("\n" + "="*60)
    print("✓ ALL GRAPH TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    test_graphs()