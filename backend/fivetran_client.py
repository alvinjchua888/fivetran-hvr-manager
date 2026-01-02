"""
Fivetran HVR 6.0 API Client
Handles authentication and API operations for Fivetran connectors
"""
import requests
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FivetranClient:
    """Client for interacting with Fivetran HVR 6.0 API"""
    
    BASE_URL = "https://api.fivetran.com/v1"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Fivetran client with API credentials
        
        Args:
            api_key: Fivetran API key
            api_secret: Fivetran API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.auth = (api_key, api_secret)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Fivetran API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Request payload
            
        Returns:
            API response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def list_connectors(self, group_id: Optional[str] = None) -> List[Dict]:
        """
        List all connectors or connectors in a specific group
        
        Args:
            group_id: Optional group ID to filter connectors
            
        Returns:
            List of connector objects
        """
        if group_id:
            endpoint = f"groups/{group_id}/connectors"
        else:
            endpoint = "connectors"
        
        response = self._make_request("GET", endpoint)
        return response.get("data", {}).get("items", [])
    
    def get_connector(self, connector_id: str) -> Dict:
        """
        Get details of a specific connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Connector details
        """
        response = self._make_request("GET", f"connectors/{connector_id}")
        return response.get("data", {})
    
    def activate_connector(self, connector_id: str) -> Dict:
        """
        Activate a connector (resume sync)
        
        Args:
            connector_id: Connector ID
            
        Returns:
            API response
        """
        data = {"paused": False}
        response = self._make_request("PATCH", f"connectors/{connector_id}", data)
        logger.info(f"Connector {connector_id} activated")
        return response.get("data", {})
    
    def pause_connector(self, connector_id: str) -> Dict:
        """
        Pause a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            API response
        """
        data = {"paused": True}
        response = self._make_request("PATCH", f"connectors/{connector_id}", data)
        logger.info(f"Connector {connector_id} paused")
        return response.get("data", {})
    
    def sync_connector(self, connector_id: str, force: bool = False) -> Dict:
        """
        Trigger a sync/refresh for a connector
        
        Args:
            connector_id: Connector ID
            force: Force resync of historical data
            
        Returns:
            API response
        """
        endpoint = f"connectors/{connector_id}/{'force' if force else 'sync'}"
        response = self._make_request("POST", endpoint)
        logger.info(f"Sync triggered for connector {connector_id}")
        return response.get("data", {})
    
    def resync_table(self, connector_id: str, schema: str, table: str) -> Dict:
        """
        Resync a specific table
        
        Args:
            connector_id: Connector ID
            schema: Schema name
            table: Table name
            
        Returns:
            API response
        """
        endpoint = f"connectors/{connector_id}/schemas/{schema}/tables/{table}/resync"
        response = self._make_request("POST", endpoint)
        logger.info(f"Resync triggered for {schema}.{table}")
        return response.get("data", {})
    
    def get_connector_schemas(self, connector_id: str) -> Dict:
        """
        Get schemas and tables for a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Schema configuration
        """
        response = self._make_request("GET", f"connectors/{connector_id}/schemas")
        return response.get("data", {})
    
    def update_connector_schema(
        self, 
        connector_id: str, 
        schema: str, 
        table: str,
        enabled: bool
    ) -> Dict:
        """
        Enable or disable a table in a schema
        
        Args:
            connector_id: Connector ID
            schema: Schema name
            table: Table name
            enabled: Enable or disable the table
            
        Returns:
            API response
        """
        endpoint = f"connectors/{connector_id}/schemas/{schema}/tables/{table}"
        data = {"enabled": enabled}
        response = self._make_request("PATCH", endpoint, data)
        logger.info(f"Table {schema}.{table} {'enabled' if enabled else 'disabled'}")
        return response.get("data", {})
    
    def list_groups(self) -> List[Dict]:
        """
        List all groups
        
        Returns:
            List of group objects
        """
        response = self._make_request("GET", "groups")
        return response.get("data", {}).get("items", [])
    
    def get_group(self, group_id: str) -> Dict:
        """
        Get details of a specific group
        
        Args:
            group_id: Group ID
            
        Returns:
            Group details
        """
        response = self._make_request("GET", f"groups/{group_id}")
        return response.get("data", {})
    
    def test_connection(self, connector_id: str) -> Dict:
        """
        Test connector connection
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Connection test results
        """
        response = self._make_request("POST", f"connectors/{connector_id}/test")
        return response.get("data", {})
