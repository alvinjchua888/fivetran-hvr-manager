"""
Streamlit Frontend for Fivetran HVR 6.0 Operations
Interactive UI for managing Fivetran connectors
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend.api import FivetranAPI

# Page configuration
st.set_page_config(
    page_title="Fivetran HVR Manager",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'api' not in st.session_state:
        st.session_state.api = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'selected_group' not in st.session_state:
        st.session_state.selected_group = None


def authenticate():
    """Handle authentication"""
    st.sidebar.header("🔐 Authentication")
    
    api_key = st.sidebar.text_input("API Key", type="password", key="api_key")
    api_secret = st.sidebar.text_input("API Secret", type="password", key="api_secret")
    
    if st.sidebar.button("Connect", type="primary"):
        if api_key and api_secret:
            try:
                st.session_state.api = FivetranAPI(api_key, api_secret)
                # Test connection by getting groups
                st.session_state.api.get_all_groups()
                st.session_state.authenticated = True
                st.sidebar.success("✅ Connected successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Authentication failed: {e}")
        else:
            st.sidebar.warning("Please provide both API Key and API Secret")


def display_connector_card(connector):
    """Display a connector card with key information"""
    status_emoji = "✅" if connector['status'] == "Active" else "⏸️"
    
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.markdown(f"### {status_emoji} {connector['name']}")
            st.caption(f"Service: {connector['service']} | ID: {connector['id']}")
        
        with col2:
            st.metric("Status", connector['status'])
            st.caption(f"Sync State: {connector.get('sync_state', 'N/A')}")
        
        with col3:
            if connector.get('last_sync'):
                st.caption(f"Last Sync: {connector['last_sync'][:19]}")
            if connector.get('failed_at'):
                st.caption(f"❌ Failed: {connector['failed_at'][:19]}")


def connectors_page():
    """Main connectors management page"""
    st.markdown('<div class="main-header">🔄 Fivetran HVR Manager</div>', unsafe_allow_html=True)
    
    # Group filter
    try:
        groups = st.session_state.api.get_all_groups()
        group_options = {"All Groups": None}
        group_options.update({g['name']: g['id'] for g in groups})
        
        selected_group_name = st.selectbox(
            "Filter by Group",
            options=list(group_options.keys())
        )
        selected_group_id = group_options[selected_group_name]
    except Exception as e:
        st.error(f"Failed to load groups: {e}")
        selected_group_id = None
    
    # Refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        refresh = st.button("🔄 Refresh", use_container_width=True)
    
    # Get connectors
    try:
        connectors = st.session_state.api.get_all_connectors(selected_group_id)
        
        if not connectors:
            st.info("No connectors found.")
            return
        
        # Summary metrics
        active_count = sum(1 for c in connectors if c['status'] == "Active")
        paused_count = sum(1 for c in connectors if c['status'] == "Paused")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Connectors", len(connectors))
        col2.metric("Active", active_count)
        col3.metric("Paused", paused_count)
        
        st.divider()
        
        # Display connectors
        for connector in connectors:
            with st.expander(f"{connector['name']} - {connector['service']}", expanded=False):
                display_connector_card(connector)
                
                st.divider()
                
                # Action buttons
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    if st.button("▶️ Activate", key=f"activate_{connector['id']}", use_container_width=True):
                        with st.spinner("Activating..."):
                            result = st.session_state.api.activate_connector(connector['id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                
                with col2:
                    if st.button("⏸️ Pause", key=f"pause_{connector['id']}", use_container_width=True):
                        with st.spinner("Pausing..."):
                            result = st.session_state.api.pause_connector(connector['id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
                
                with col3:
                    if st.button("🔄 Sync", key=f"sync_{connector['id']}", use_container_width=True):
                        with st.spinner("Starting sync..."):
                            result = st.session_state.api.sync_connector(connector['id'])
                            if result['success']:
                                st.success(result['message'])
                            else:
                                st.error(result['message'])
                
                with col4:
                    if st.button("⚡ Force Sync", key=f"force_{connector['id']}", use_container_width=True):
                        with st.spinner("Starting force sync..."):
                            result = st.session_state.api.sync_connector(connector['id'], force=True)
                            if result['success']:
                                st.success(result['message'])
                            else:
                                st.error(result['message'])
                
                with col5:
                    if st.button("📊 Details", key=f"details_{connector['id']}", use_container_width=True):
                        st.session_state.selected_connector = connector['id']
                        st.session_state.page = "details"
                        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to load connectors: {e}")


def connector_details_page():
    """Detailed connector view"""
    if 'selected_connector' not in st.session_state:
        st.warning("No connector selected")
        if st.button("← Back to Connectors"):
            st.session_state.page = "connectors"
            st.rerun()
        return
    
    connector_id = st.session_state.selected_connector
    
    if st.button("← Back to Connectors"):
        st.session_state.page = "connectors"
        st.rerun()
    
    st.markdown(f'<div class="main-header">📊 Connector Details</div>', unsafe_allow_html=True)
    
    try:
        # Get connector details
        details = st.session_state.api.get_connector_details(connector_id)
        
        # Basic Information
        st.subheader("Basic Information")
        col1, col2, col3 = st.columns(3)
        col1.metric("Name", details.get('name', 'N/A'))
        col2.metric("Service", details.get('service', 'N/A'))
        col3.metric("Status", "Active" if not details.get('paused') else "Paused")
        
        # Sync Information
        st.subheader("Sync Information")
        col1, col2, col3 = st.columns(3)
        col1.metric("Sync State", details.get('sync_state', 'N/A'))
        col2.metric("Setup State", details.get('setup_state', 'N/A'))
        col3.metric("Update State", details.get('update_state', 'N/A'))
        
        if details.get('succeeded_at'):
            st.info(f"Last successful sync: {details['succeeded_at']}")
        if details.get('failed_at'):
            st.error(f"Last failed at: {details['failed_at']}")
        
        # Schedule Information
        st.subheader("Schedule Configuration")
        col1, col2 = st.columns(2)
        col1.metric("Schedule Type", details.get('schedule_type', 'N/A'))
        col2.metric("Sync Frequency (minutes)", details.get('sync_frequency', 'N/A'))
        
        # Schemas and Tables
        st.subheader("Schemas and Tables")
        
        if st.button("🔄 Load Schemas"):
            with st.spinner("Loading schemas..."):
                schemas_result = st.session_state.api.get_connector_schemas(connector_id)
                
                if schemas_result['success']:
                    schemas_data = schemas_result['data'].get('schemas', {})
                    
                    if schemas_data:
                        for schema_name, schema_info in schemas_data.items():
                            with st.expander(f"Schema: {schema_name}", expanded=False):
                                tables = schema_info.get('tables', {})
                                
                                if tables:
                                    table_data = []
                                    for table_name, table_info in tables.items():
                                        table_data.append({
                                            'Table': table_name,
                                            'Enabled': table_info.get('enabled', False),
                                            'Sync Mode': table_info.get('sync_mode', 'N/A')
                                        })
                                    
                                    df = pd.DataFrame(table_data)
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # Table actions
                                    st.caption("Table Operations")
                                    selected_table = st.selectbox(
                                        "Select Table",
                                        options=[t['Table'] for t in table_data],
                                        key=f"table_select_{schema_name}"
                                    )
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if st.button("🔄 Resync", key=f"resync_{schema_name}_{selected_table}"):
                                            result = st.session_state.api.resync_table(
                                                connector_id, schema_name, selected_table
                                            )
                                            if result['success']:
                                                st.success(result['message'])
                                            else:
                                                st.error(result['message'])
                                    
                                    with col2:
                                        if st.button("✅ Enable", key=f"enable_{schema_name}_{selected_table}"):
                                            result = st.session_state.api.toggle_table(
                                                connector_id, schema_name, selected_table, True
                                            )
                                            if result['success']:
                                                st.success(result['message'])
                                            else:
                                                st.error(result['message'])
                                    
                                    with col3:
                                        if st.button("❌ Disable", key=f"disable_{schema_name}_{selected_table}"):
                                            result = st.session_state.api.toggle_table(
                                                connector_id, schema_name, selected_table, False
                                            )
                                            if result['success']:
                                                st.success(result['message'])
                                            else:
                                                st.error(result['message'])
                                else:
                                    st.info("No tables found in this schema")
                    else:
                        st.info("No schemas found")
                else:
                    st.error(schemas_result['message'])
        
        # Connection Test
        st.subheader("Connection Test")
        if st.button("🔍 Test Connection"):
            with st.spinner("Testing connection..."):
                result = st.session_state.api.test_connection(connector_id)
                if result['success']:
                    st.success(result['message'])
                    if result.get('data'):
                        st.json(result['data'])
                else:
                    st.error(result['message'])
    
    except Exception as e:
        st.error(f"Failed to load connector details: {e}")


def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.fivetran.com/wp-content/themes/fivetran-2021/images/fivetran-logo.svg", width=150)
        st.title("Navigation")
    
    # Authentication
    if not st.session_state.authenticated:
        authenticate()
        
        # Welcome message
        st.markdown('<div class="main-header">🔄 Fivetran HVR Manager</div>', unsafe_allow_html=True)
        st.markdown("""
        ### Welcome to Fivetran HVR Manager
        
        This application allows you to manage your Fivetran HVR 6.0 connectors with an intuitive interface.
        
        **Features:**
        - 📋 View all connectors and their status
        - ▶️ Activate/Pause connectors
        - 🔄 Trigger sync and force sync operations
        - 📊 View detailed connector information
        - 🗂️ Manage schemas and tables
        - ⚡ Resync specific tables
        - 🔍 Test connector connections
        
        **Getting Started:**
        1. Enter your Fivetran API Key and Secret in the sidebar
        2. Click "Connect" to authenticate
        3. Start managing your connectors!
        
        ---
        
        ℹ️ Need API credentials? Visit [Fivetran Dashboard](https://fivetran.com/dashboard/account/api)
        """)
        return
    
    # Navigation
    if 'page' not in st.session_state:
        st.session_state.page = "connectors"
    
    with st.sidebar:
        st.success("✅ Connected")
        
        if st.button("📋 Connectors", use_container_width=True):
            st.session_state.page = "connectors"
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Disconnect", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.api = None
            st.rerun()
    
    # Page routing
    if st.session_state.page == "connectors":
        connectors_page()
    elif st.session_state.page == "details":
        connector_details_page()


if __name__ == "__main__":
    main()
