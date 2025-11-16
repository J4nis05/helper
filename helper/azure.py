from typing import Optional, Dict, Any

from helper import BaseGraphClient


class AzureConnection(BaseGraphClient):
    """Azure Resource Manager API client for managing Azure resources."""
    
    def __init__(
        self,
        tenant: str, 
        client: str, 
        secret: str,
        scope: str = "https://management.azure.com/.default",
        api_version: str = "2020-01-01",
        **kwargs
    ):
        super().__init__(
            tenant=tenant, 
            client=client, 
            secret=secret, 
            scope=scope,
            api_url="https://management.azure.com", 
            api_version=api_version, 
            **kwargs,
        )

    def get_subscriptions(self) -> dict:
        """Get all subscriptions."""
        return self.get_request("subscriptions")

    def get_subscription(self, subscription_id: str) -> dict:
        """Get a specific subscription."""
        return self.get_request(f"subscriptions/{subscription_id}")

    def get_resource_groups(self, subscription_id: str) -> dict:
        """Get all resource groups in a subscription."""
        return self.get_request(f"subscriptions/{subscription_id}/resourcegroups")

    def get_resources(self, subscription_id: str, resource_group: Optional[str] = None) -> dict:
        """Get resources in a subscription or resource group."""
        if resource_group:
            return self.get_request(f"subscriptions/{subscription_id}/resourceGroups/{resource_group}/resources")
        return self.get_request(f"subscriptions/{subscription_id}/resources")

    def get_resource(self, resource_id: str) -> dict:
        """Get a specific resource by its full resource ID."""
        return self.get_request(f"{resource_id}")

    def get_all_pages(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Aggregate all pages from paginated Azure API responses."""
        result = {"value": []}
        page = self.get_request(endpoint, params=params)
        while page:
            vals = page.get("value")
            if isinstance(vals, list):
                result["value"].extend(vals)
            next_link = page.get("@odata.nextLink") or page.get("nextLink")
            if not next_link:
                break
            page = self._request("GET", next_link.replace(f"{self.api_url}/{self.api_version}/", ""))
        return result