from typing import Any, Dict, Optional, Union
import json

import requests
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from helper import Util, FileHandler
from helper import get_graph_token


class BaseGraphClient:
    def __init__(self,
        tenant: str, client: str, secret: str, scope: str,
        api_url: str, api_version: str, timeout: Union[float, tuple] = 30.0,
        enable_retries: bool = True, max_retries: int = 3, backoff_factor: float = 0.5, raise_on_error: bool = False
    ):
        self.tenant = tenant
        self.client = client
        self.secret = secret
        self.scope = scope

        self.api_url = api_url.rstrip("/")
        self.api_version = api_version.strip("/")

        self.token, self.auth_response = get_graph_token(
            self.tenant, self.client, self.secret, self.scope
        )
        self.header = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        self.timeout = timeout
        self.raise_on_error = raise_on_error

        self.ntfs_reserved = ['<', '>', ':', '"', '/', "\\", "|", "?", "*"]
        self.history: Dict[str, Dict[str, Any]] = {}

        self.session: Session = requests.Session()
        if enable_retries:
            retry = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)


    def get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        return self._request("GET", endpoint, params=params)

    def post_request(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the API."""
        return self._request("POST", endpoint, json_body=body)

    def put_request(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        return self._request("PUT", endpoint, json_body=body)

    def patch_request(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request to the API."""
        return self._request("PATCH", endpoint, json_body=body)

    def delete_request(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        return self._request("DELETE", endpoint, json_body=body)

    def _request(
        self,
        method: str, 
        endpoint: str, *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        # URL Build
        endpoint = endpoint.lstrip("/")
        url = f"{self.api_url}/{self.api_version}/{endpoint}"
        if params:
            query = Util.build_query(params)
            if query:
                url = f"{url}?{query}"

        # Request Content Build
        headers = dict(self.header)
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        # For Later
        t_key = str(Util.unix_timestamp())
        response: Optional[Response] = None
        response_json: Dict[str, Any] = {}
        error_info: Optional[str] = None

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                timeout=self.timeout
            )

            if response.status_code == 401 and self._maybe_refresh_token():
                headers["Authorization"] = f"Bearer {self.token}"
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body,
                    timeout=self.timeout
                )

            response.raise_for_status()
            response_json = self._safe_json(response)

        except Exception as e:
            error_info = str(e)

            if response is not None and not response_json:
                text = response.text
                response_json = {"_non_json_body": text[:4000]}

            if self.raise_on_error:
                raise

        self.history[t_key] = {
            "request_url"    : url,
            "request_header" : headers,
            "request_method" : method,
            "request_body"   : json_body,
            "response_status": response.status_code if response else None,
            "response_header": dict(response.headers) if response else {},
            "response_json"  : response_json,
            "error"          : error_info,
        }

        return response_json

    def _safe_json(self, response: Response) -> Dict[str, Any]:
        """Safely JSON deserialize and return a dict."""
        if not response.content or response.status_code == 204:
            return {}
        try:
            return response.json()
        except Exception:
            return {"_non_json_body": response.text[:4000]}

    def _maybe_refresh_token(self) -> bool:
        """Refresh token if needed."""
        try:
            new_token, _ = get_graph_token(
                self.tenant, self.client, self.secret, self.scope
            )
            if new_token and new_token != self.token:
                self.token = new_token
                self.header["Authorization"] = f"Bearer {self.token}"
                return True
        except Exception:
            pass
        return False

    def save_history(self, path: str) -> list:
        """Save request history to JSON files in the specified directory."""
        paths = []

        # Moving Old Files
        if not FileHandler.verify(f"{path}/old"):
            FileHandler.mkdir(f"{path}/old")
        files = FileHandler.scan(path)
        for file in files:
            if file.endswith(".json"):
                _, filename, extension = FileHandler.split(file)
                FileHandler.move(FileHandler.join([file]), FileHandler.join([path, "old", f"{filename}{extension}"]))
        
        # Saving Files
        for key, data in self.history.items():
            url = data.get("request_url", "")
            safe_url = url.replace(f"{self.api_url}/", "").replace("/", "_")
            for character in self.ntfs_reserved:
                safe_url = safe_url.replace(character, "_")

            if len(safe_url) > 150:
                safe_url = safe_url[:150]

            filename = f"{key}_{safe_url}.json"
            save_path = FileHandler.join([path, filename])

            content = json.dumps(data, indent=4, ensure_ascii=False)
            FileHandler.write(save_path, content)
            paths.append(save_path)
        return paths