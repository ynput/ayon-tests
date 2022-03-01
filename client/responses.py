import json
import http


class RestResponse:
    """REST API Response."""

    def __init__(self, status: int = 200, **data):
        self.status = status
        self.data = data

    @property
    def detail(self):
        return self.get(
            "detail",
            http.HTTPStatus(self.status).description
        )

    def __repr__(self) -> str:
        return f"<RestResponse: {self.status} ({self.detail})>"

    def __len__(self):
        return 200 <= self.status < 400

    def __getitem__(self, key: str):
        return self.data[key]

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def print(self):
        print(json.dumps(self.data, indent=4))


class GraphQLResponse:
    """GraphQLResponse"""

    def __init__(self, **response):
        if "code" in response:
            # got rest response instead of gql (maybe unauthorized)
            self.data = {}
            self.errors = [{"message": response["detail"]}]
        else:
            self.data = response.get("data", {})
            self.errors = response.get("errors", [])

    def __len__(self):
        return not bool(self.errors)

    def __repr__(self):
        if self.errors:
            msg = f"errors=\"{self.errors[0]['message']}\""
        else:
            msg = "status=\"OK\">"
        return f"<GraphQLResponse: {msg}>"

    def __getitem__(self, key):
        return self.data[key]
