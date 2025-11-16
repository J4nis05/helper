from helper import BaseGraphClient

class DefenderConnection(BaseGraphClient):
    """Microsoft Defender for Endpoint API client."""
    
    def __init__(self, tenant: str, client: str, secret: str, **kwargs):
        super().__init__(
            tenant=tenant,
            client=client,
            secret=secret,
            scope="https://api.securitycenter.microsoft.com/.default",
            api_url="https://api.securitycenter.microsoft.com",
            api_version="api",
            **kwargs
        )