# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Send a custom request to the Zendesk Support API."""

import json

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..app import Asset, app
from ..helper import request as zendesk_request


class MakeRequestParams(Params):
    method: str = Param(description="HTTP method: GET, POST, PUT, PATCH, or DELETE")
    endpoint: str = Param(description="Zendesk API endpoint, such as /tickets.json")
    query_params: str | None = Param(
        description="Optional query parameters as a JSON object"
    )
    body: str | None = Param(description="Optional request body as JSON")


class MakeRequestOutput(ActionOutput):
    response: str = OutputField(column_name="Response")


@app.action(
    description="Send a custom request to the Zendesk Support API",
    action_type="generic",
    read_only=False,
)
def make_request(
    params: MakeRequestParams, soar: SOARClient, asset: Asset
) -> MakeRequestOutput:
    """Send one request to the configured Zendesk API and return its response."""
    method = params.method.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        raise ActionFailure("method must be GET, POST, PUT, PATCH, or DELETE")
    if (
        not params.endpoint.startswith("/")
        or params.endpoint.startswith("//")
        or ".." in params.endpoint.split("/")
    ):
        raise ActionFailure("endpoint must be a path under the Zendesk API")
    try:
        query = json.loads(params.query_params) if params.query_params else None
        body = json.loads(params.body) if params.body else None
    except ValueError as exc:
        raise ActionFailure("query_params and body must contain valid JSON") from exc
    if query is not None and not isinstance(query, dict):
        raise ActionFailure("query_params must be a JSON object")
    payload = zendesk_request(asset, method, params.endpoint, params=query, data=body)
    return MakeRequestOutput(response=json.dumps(payload))
