# Fivetran HVR 6.0 Manager

A Python backend with Streamlit frontend for managing Fivetran HVR 6.0 connectors.

## Features

### Connector Management
- **View Connectors**: List all connectors with their current status
- **Activate/Pause**: Control connector execution
- **Sync Operations**: Trigger regular sync or force historical resync
- **Connection Testing**: Verify connector connectivity

### Schema Management
- **View Schemas**: Browse all schemas and tables for each connector
- **Table Operations**: Enable/disable specific tables
- **Resync Tables**: Trigger resync for individual tables

### User Interface
- **Group Filtering**: Filter connectors by group
- **Real-time Status**: View sync state, setup state, and last sync times
- **Detailed Views**: Deep dive into connector configurations
- **Bulk Operations**: Manage multiple connectors efficiently

## Architecture

### Backend (`backend/`)
- **fivetran_client.py**: Low-level API client for Fivetran HVR 6.0 API
- **api.py**: High-level API wrapper with business logic

### Frontend
- **app.py**: Streamlit application with interactive UI

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Get Fivetran API credentials**:
   - Log in to Fivetran Dashboard
   - Navigate to Settings → API Config
   - Generate API Key and Secret

## Usage

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Access the UI**:
   - Open browser to `http://localhost:8501`

3. **Authenticate**:
   - Enter API Key and Secret in sidebar
   - Click "Connect"

4. **Manage Connectors**:
   - View all connectors in main page
   - Click on connector to expand operations
   - Use action buttons for operations
   - Click "Details" for detailed view

## API Operations

### Connector Operations
- `list_connectors()` - List all connectors
- `get_connector(connector_id)` - Get connector details
- `activate_connector(connector_id)` - Resume sync
- `pause_connector(connector_id)` - Pause sync
- `sync_connector(connector_id, force)` - Trigger sync
- `test_connection(connector_id)` - Test connection

### Schema Operations
- `get_connector_schemas(connector_id)` - Get schemas and tables
- `update_connector_schema(...)` - Enable/disable tables
- `resync_table(connector_id, schema, table)` - Resync specific table

### Group Operations
- `list_groups()` - List all groups
- `get_group(group_id)` - Get group details

## Configuration

The application uses Fivetran's REST API v1 endpoint:
```
https://api.fivetran.com/v1
```

Authentication uses HTTP Basic Auth with API Key and Secret.

## Security Notes

- API credentials are stored only in session state
- Credentials are not persisted to disk
- Use environment variables or secrets management for production
- Never commit credentials to version control

## Error Handling

The application includes comprehensive error handling:
- API request failures
- Authentication errors
- Network timeouts
- Invalid operations

## Troubleshooting

### Authentication Issues
- Verify API Key and Secret are correct
- Check API key has necessary permissions
- Ensure network connectivity to Fivetran API

### Connection Errors
- Check connector status in Fivetran Dashboard
- Verify connector is properly configured
- Review connector error logs

### Sync Issues
- Check if connector is paused
- Verify schema/table configurations
- Review sync history in Fivetran Dashboard

## API Reference

Fivetran HVR 6.0 API Documentation:
- [API Reference](https://fivetran.com/docs/rest-api)
- [Authentication](https://fivetran.com/docs/rest-api/getting-started)
- [Connectors API](https://fivetran.com/docs/rest-api/connectors)

## License

MIT License

## Support

For issues related to:
- **Application**: Create an issue in this repository
- **Fivetran API**: Contact Fivetran support
- **HVR Specific**: Check Fivetran HVR documentation
