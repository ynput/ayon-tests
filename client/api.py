import json
import simplejson  # just because of the exceptions
import requests

from nxtools import logging

from .responses import RestResponse, GraphQLResponse


class API:
    """OpenPype API client"""

    def __init__(
        self,
        server_url: str,
        access_token: str,
        debug: bool = False
    ):
        self.server_url = server_url.rstrip("/")
        self.access_token = access_token
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })

    @classmethod
    def login(
        cls,
        name: str,
        password: str,
        server_url: str = "http://localhost:5000",
    ) -> 'API':
        server_url = server_url.rstrip("/")
        response = requests.post(
            server_url + "/api/auth/login",
            json={
                "name": name,
                "password": password
            }
        )
        data = response.json()
        return cls(server_url, data.get("token", "NotAuthorizedToken"))

    def logout(self):
        if not self.access_token:
            return
        return self.post("auth/logout")

    def gql(self, query, **kwargs):
        """Execute a GraphQL query."""
        payload = {
            "query": query,
            "variables": kwargs
        }
        response = self.session.post(
            self.server_url + "/graphql",
            json=payload
        )
        return GraphQLResponse(**response.json())

    def _request(self, function: callable, url: str, **kwargs):
        """Do an authenticated HTTP request.

        This private method is used by get/post/put/patch/delete
        """
        try:
            response = function(url, **kwargs)
        except ConnectionRefusedError:
            response = RestResponse(
                500,
                detail="Unable to connect the server. Connection refused"
            )
        except requests.exceptions.ConnectionError:
            response = RestResponse(
                500,
                detail="Unable to connect the server. Connection error"
            )
        else:
            if response.text == "":
                data = None
                response = RestResponse(response.status_code)
            else:
                try:
                    data = response.json()
                except (
                    json.JSONDecodeError,
                    simplejson.errors.JSONDecodeError
                ):
                    logging.error(response.text)
                    response = RestResponse(
                        500,
                        detail=f"The response is not a JSON: {response.text}"
                    )
                else:
                    response = RestResponse(response.status_code, **data)
        if self.debug:
            if response:
                logging.goodnews(response)
            else:
                logging.error(response)
        return response

    def get(self, endpoint: str, **kwargs) -> RestResponse:
        endpoint = endpoint.strip("/")
        if self.debug:
            logging.info(f"Executing [GET] {endpoint}")
        url = f"{self.server_url}/api/{endpoint}"
        return self._request(self.session.get, url, params=kwargs)

    def post(self, endpoint: str, **kwargs) -> RestResponse:
        endpoint = endpoint.strip("/")
        if self.debug:
            logging.info(f"Executing [POST] {endpoint}")
        url = f"{self.server_url}/api/{endpoint}"
        return self._request(self.session.post, url, json=kwargs)

    def put(self, endpoint: str, **kwargs) -> RestResponse:
        endpoint = endpoint.strip("/")
        if self.debug:
            logging.info(f"Executing [PUT] {endpoint}")
        url = f"{self.server_url}/api/{endpoint}"
        return self._request(self.session.put, url, json=kwargs)

    def patch(self, endpoint: str, **kwargs) -> RestResponse:
        endpoint = endpoint.strip("/")
        if self.debug:
            logging.info(f"Executing [PATCH] {endpoint}")
        url = f"{self.server_url}/api/{endpoint}"
        return self._request(self.session.patch, url, json=kwargs)

    def delete(self, endpoint: str, **kwargs) -> RestResponse:
        endpoint = endpoint.strip("/")
        if self.debug:
            logging.info(f"Executing [DELETE] {endpoint}")
        url = f"{self.server_url}/api/{endpoint}"
        return self._request(self.session.delete, url, params=kwargs)
