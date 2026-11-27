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
from collections.abc import Sequence
from urllib.parse import parse_qsl

from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams

from ..asset import Asset
from ..helper import request as zendesk_request


class MakeRequestOutput(ActionOutput):
    response: str = OutputField(column_name="Response")


def _parse_query_parameters(value: str | None) -> Sequence[tuple[str, object]]:
    if not value:
        return []
    if not value.lstrip().startswith(("{", "[")):
        return parse_qsl(value.lstrip("?"), keep_blank_values=True)

    error_message = "query_parameters must be a JSON object or a query string"
    try:
        query = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ActionFailure(error_message) from exc
    if not isinstance(query, dict):
        raise ActionFailure(error_message)
    return list(query.items())


def make_request(params: MakeRequestParams, asset: Asset) -> MakeRequestOutput:
    """Send a custom request to the Zendesk Support API"""
    method = params.http_method.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
        raise ActionFailure(
            "http_method must be GET, POST, PUT, PATCH, DELETE, HEAD, or OPTIONS"
        )
    if (
        not params.endpoint.startswith("/")
        or params.endpoint.startswith("//")
        or ".." in params.endpoint.split("/")
    ):
        raise ActionFailure("endpoint must be a path under the Zendesk API")
    query = _parse_query_parameters(params.query_parameters)
    try:
        headers = json.loads(params.headers) if params.headers else {}
        body = json.loads(params.body) if params.body else None
    except json.JSONDecodeError as exc:
        raise ActionFailure("headers and body must contain valid JSON") from exc
    if not isinstance(headers, dict) or not all(
        isinstance(value, str) for value in headers.values()
    ):
        raise ActionFailure("headers must be a JSON object with string values")
    payload = zendesk_request(
        asset,
        method,
        params.endpoint,
        params=query,
        data=body,
        headers=headers,
        timeout=params.timeout if params.timeout is not None else 30,
        verify_ssl=params.verify_ssl,
    )
    return MakeRequestOutput(response=json.dumps(payload))
