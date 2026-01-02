"""
Backend API for Fivetran HVR operations
Provides endpoints for Streamlit frontend
"""
from typing import Dict, List, Optional, Any
from fivetran_client import FivetranClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FivetranAPI:
    """Backend API wrapper for Fivetran operations"""
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize backend API
        
        Args:
            api_key: Fivetran API key
            api_secret: Fivetran API secret
        """
        self.client = FivetranClient(api_key, api_secret)
    
    def get_all_connectors(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all connectors with formatted information
        
        Args:
            group_id: Optional group ID filter
            
        Returns:
            List of formatted connector information
        """
        try:
            connectors = self.client.list_connectors(group_id)
            formatted = []
            
            for connector in connectors:
                formatted.append({
                    "id": connector.get("id"),
                    "name": connector.get("schema"),
                    "service": connector.get("service"),
                    "status": "Active" if not connector.get("paused") else "Paused",
                    "sync_state": connector.get("status", {}).get("sync_state"),
                    "setup_state": connector.get("status", {}).get("setup_state"),
                    "last_sync": connector.get("succeeded_at"),
                    "failed_at": connector.get("failed_at"),
                    "paused": connector.get("paused", False),
                    "group_id": connector.get("group_id")
                })
            
            return formatted
        except Exception as e:
            logger.error(f"Failed to get connectors: {e}")
            raise
    
    def get_connector_details(self, connector_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Connector details
        """
        try:
            connector = self.client.get_connector(connector_id)
            return {
                "id": connector.get("id"),
                "name": connector.get("schema"),
                "service": connector.get("service"),
                "paused": connector.get("paused"),
                "sync_frequency": connector.get("sync_frequency"),
                "daily_sync_time": connector.get("daily_sync_time"),
                "schedule_type": connector.get("schedule_type"),
                "status": connector.get("status"),
                "setup_state": connector.get("status", {}).get("setup_state"),
                "sync_state": connector.get("status", {}).get("sync_state"),
                "update_state": connector.get("status", {}).get("update_state"),
                "succeeded_at": connector.get("succeeded_at"),
                "failed_at": connector.get("failed_at"),
                "config": connector.get("config"),
                "group_id": connector.get("group_id")
            }
        except Exception as e:
            logger.error(f"Failed to get connector details: {e}")
            raise
    
    def activate_connector(self, connector_id: str) -> Dict[str, Any]:
        """
        Activate/resume a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Result of activation
        """
        try:
            result = self.client.activate_connector(connector_id)
            return {"success": True, "message": f"Connector activated", "data": result}
        except Exception as e:
            logger.error(f"Failed to activate connector: {e}")
            return {"success": False, "message": str(e)}
    
    def pause_connector(self, connector_id: str) -> Dict[str, Any]:
        """
        Pause a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Result of pause operation
        """
        try:
            result = self.client.pause_connector(connector_id)
            return {"success": True, "message": f"Connector paused", "data": result}
        except Exception as e:
            logger.error(f"Failed to pause connector: {e}")
            return {"success": False, "message": str(e)}
    
    def sync_connector(self, connector_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Trigger sync/refresh for a connector
        
        Args:
            connector_id: Connector ID
            force: Force historical resync
            
        Returns:
            Result of sync operation
        """
        try:
            result = self.client.sync_connector(connector_id, force)
            sync_type = "force sync" if force else "sync"
            return {"success": True, "message": f"Connector {sync_type} triggered", "data": result}
        except Exception as e:
            logger.error(f"Failed to sync connector: {e}")
            return {"success": False, "message": str(e)}
    
    def get_connector_schemas(self, connector_id: str) -> Dict[str, Any]:
        """
        Get schemas and tables for a connector
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Schema configuration
        """
        try:
            schemas = self.client.get_connector_schemas(connector_id)
            return {"success": True, "data": schemas}
        except Exception as e:
            logger.error(f"Failed to get schemas: {e}")
            return {"success": False, "message": str(e)}
    
    def resync_table(self, connector_id: str, schema: str, table: str) -> Dict[str, Any]:
        """
        Resync a specific table
        
        Args:
            connector_id: Connector ID
            schema: Schema name
            table: Table name
            
        Returns:
            Result of resync operation
        """
        try:
            result = self.client.resync_table(connector_id, schema, table)
            return {"success": True, "message": f"Table {schema}.{table} resync triggered", "data": result}
        except Exception as e:
            logger.error(f"Failed to resync table: {e}")
            return {"success": False, "message": str(e)}
    
    def toggle_table(
        self, 
        connector_id: str, 
        schema: str, 
        table: str, 
        enabled: bool
    ) -> Dict[str, Any]:
        """
        Enable or disable a table
        
        Args:
            connector_id: Connector ID
            schema: Schema name
            table: Table name
            enabled: Enable or disable
            
        Returns:
            Result of operation
        """
        try:
            result = self.client.update_connector_schema(connector_id, schema, table, enabled)
            status = "enabled" if enabled else "disabled"
            return {"success": True, "message": f"Table {schema}.{table} {status}", "data": result}
        except Exception as e:
            logger.error(f"Failed to toggle table: {e}")
            return {"success": False, "message": str(e)}
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        """
        Get all groups
        
        Returns:
            List of groups
        """
        try:
            groups = self.client.list_groups()
            formatted = []
            
            for group in groups:
                formatted.append({
                    "id": group.get("id"),
                    "name": group.get("name"),
                    "created_at": group.get("created_at")
                })
            
            return formatted
        except Exception as e:
            logger.error(f"Failed to get groups: {e}")
            raise
    
    def test_connection(self, connector_id: str) -> Dict[str, Any]:
        """
        Test connector connection
        
        Args:
            connector_id: Connector ID
            
        Returns:
            Connection test results
        """
        try:
            result = self.client.test_connection(connector_id)
            return {"success": True, "message": "Connection test completed", "data": result}
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return {"success": False, "message": str(e)}
