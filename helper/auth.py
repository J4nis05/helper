import urllib.parse
import urllib.request
import json
from typing import Tuple, Dict

DEFAULT_TIMEOUT = 30.0


def get_token(tenant_id: str, client_id: str, client_secret: str, resource_url: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[str, Dict]:
    """Get OAuth2 token for legacy Azure AD endpoints."""
    # https://learn.microsoft.com/en-us/defender-endpoint/api/run-advanced-query-sample-python#get-token
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    body = {
        'resource': resource_url,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    request_data  = urllib.parse.urlencode(body).encode("utf-8")
    request = urllib.request.Request(url, request_data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        json_response = json.loads(response.read())
    aad_token = json_response["access_token"]

    return aad_token, json_response


def get_graph_token(tenant_id: str, client_id: str, client_secret: str, scope: str = "https://graph.microsoft.com/.default", timeout: float = DEFAULT_TIMEOUT) -> Tuple[str, Dict]:
    """Get OAuth2 token for Microsoft Graph API."""

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "scope": scope,
            "client_secret": client_secret,
        }
    ).encode()

    request = urllib.request.Request(url, headers=header, data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        json_response = json.loads(response.read())
    graph_token = json_response["access_token"]

    return graph_token, json_response


def refresh_token(tenant_id: str, client_id: str, client_secret: str, refresh_token: str, scope: str = "https://graph.microsoft.com/.default", timeout: float = DEFAULT_TIMEOUT) -> Tuple[str, str, Dict]:
    """Refresh an OAuth2 token using a refresh token."""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "scope": scope,
        }
    ).encode()

    request = urllib.request.Request(url, headers=header, data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        json_response = json.loads(response.read())
    access_token = json_response["access_token"]
    new_refresh_token = json_response.get("refresh_token", refresh_token)  # Use new one if provided, else keep old
    
    return access_token, new_refresh_token, json_response