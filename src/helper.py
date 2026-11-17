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
"""Shared Zendesk REST helpers."""

import json
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from soar_sdk.auth import BasicAuth
from soar_sdk.exceptions import ActionFailure


def request(asset, method: str, endpoint: str, *, params=None, data=None):
    """Call Zendesk and return its JSON response, raising useful API errors."""
    parsed_url = urlsplit(asset.url)
    if parsed_url.scheme.lower() != "https" or not parsed_url.netloc:
        raise ActionFailure("Zendesk API URL must be a valid HTTPS URL")
    base_url = asset.url.rstrip("/") + "/api/v2"
    secret = asset.password or asset.api_token
    if not secret:
        raise ActionFailure("Please specify one of either 'Password' or 'API Token'")
    username = asset.username + (
        "/token" if asset.api_token and not asset.password else ""
    )
    url = f"{base_url}{endpoint}"
    if params:
        parsed_endpoint = urlsplit(url)
        extra_query = urlencode(params, doseq=True)
        combined_query = "&".join(
            part for part in (parsed_endpoint.query, extra_query) if part
        )
        url = urlunsplit(parsed_endpoint._replace(query=combined_query))

    try:
        response = httpx.request(
            method,
            url,
            auth=BasicAuth(username, secret),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=data,
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise ActionFailure(f"Unable to connect to Zendesk: {exc}") from exc
    if response.status_code == 204:
        return None
    try:
        payload = response.json()
    except ValueError as exc:
        raise ActionFailure("Unable to parse response as JSON") from exc
    if not 200 <= response.status_code < 400:
        raise ActionFailure(
            f"Zendesk API error ({response.status_code}): {json.dumps(payload)}"
        )
    return payload


def ticket_output(output_cls, ticket, result_status="success"):
    """Build an output model without rejecting API fields absent from a response."""
    output = dict(ticket)
    if "result_status" in output_cls.model_fields:
        output["result_status"] = result_status
    return output_cls.model_construct(**output)


def enrich_ticket_user_names(asset, tickets):
    """Add submitter, assignee, and requester names as the legacy connector did."""
    name_cache = {}
    for ticket in tickets:
        for id_field in ("submitter_id", "assignee_id", "requester_id"):
            user_id = ticket.get(id_field)
            if user_id is None:
                continue
            name_field = f"{id_field}_name"
            if user_id not in name_cache:
                try:
                    user_payload = request(asset, "GET", f"/users/{user_id}.json")
                except (ActionFailure, httpx.HTTPError, ValueError):
                    name_cache[user_id] = None
                else:
                    user_cache = user_payload.get("user") or {}
                    name_cache[user_id] = user_cache.get("name")
            if name_cache[user_id]:
                ticket[name_field] = name_cache[user_id]
    return tickets


def resolve_custom_fields(asset, custom_fields):
    """Translate legacy title/value custom fields to Zendesk ID/value entries."""
    if not isinstance(custom_fields, list):
        raise ActionFailure("Invalid value for custom_field")

    base_url = urlsplit(asset.url)
    endpoint = "/ticket_fields.json"
    params = {"per_page": 100}
    ticket_fields = []
    seen_pages = set()

    while endpoint:
        page = (endpoint, tuple(sorted(params.items())))
        if page in seen_pages:
            raise ActionFailure(
                "Unable to safely retrieve the complete ticket field catalog"
            )
        seen_pages.add(page)
        response = request(asset, "GET", endpoint, params=params)
        ticket_fields.extend(response.get("ticket_fields", []))

        next_page = response.get("next_page")
        if not next_page:
            break
        next_page_url = urlsplit(next_page)
        if (
            next_page_url.scheme != base_url.scheme
            or next_page_url.netloc != base_url.netloc
            or not next_page_url.path.startswith("/api/v2/")
        ):
            raise ActionFailure(
                "Unable to safely retrieve the complete ticket field catalog"
            )
        endpoint = next_page_url.path[len("/api/v2") :]
        params = dict(parse_qsl(next_page_url.query, keep_blank_values=True))

    fields_by_title = {
        field.get("raw_title"): field.get("id")
        for field in ticket_fields
        if field.get("raw_title") is not None and field.get("id") is not None
    }
    converted = []
    unmatched = []
    for item in custom_fields:
        if not isinstance(item, dict) or len(item) != 1:
            raise ActionFailure("Invalid value for custom_field")
        title, value = next(iter(item.items()))
        field_id = fields_by_title.get(title)
        if field_id is None:
            unmatched.append(str(title))
        else:
            converted.append({"id": field_id, "value": value})
    if unmatched:
        raise ActionFailure(
            "Unable to resolve ticket custom field title(s): " + ", ".join(unmatched)
        )
    return converted
