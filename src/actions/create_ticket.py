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
"""Zendesk create_ticket action."""

import json

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import (
    ActionOutput,
    ActionResult,
    OutputField,
    PermissiveActionOutput,
)
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..helper import (
    enrich_ticket_user_names,
    request as zendesk_request,
    resolve_custom_fields,
)


class CreateTicketParams(Params):
    subject: str = Param(description="Ticket Subject")
    description: str = Param(description="Ticket Description")
    fields: str | None = Param(description="Json containing field values")


class CustomFieldsOutput(PermissiveActionOutput):
    """Preserve values whose types vary by Zendesk custom-field configuration."""

    id: int = OutputField(example_values=[360011869194])


class FieldsOutput(PermissiveActionOutput):
    """Preserve values whose types vary by Zendesk custom-field configuration."""

    id: int = OutputField(example_values=[360011869194])


class SourceOutput(ActionOutput):
    rel: str | None


class ViaOutput(ActionOutput):
    channel: str = OutputField(example_values=["api"])
    source: SourceOutput | None


class CreateTicketOutput(PermissiveActionOutput):
    """Preserve raw brand_id, recipient, and satisfaction_rating values.

    Zendesk returns multiple types for these fields, which the SOAR manifest
    cannot describe.
    """

    id: int = OutputField(
        column_name="ID", cef_types=["zendesk ticket id"], example_values=[1189]
    )
    url: str = OutputField(
        column_name="URL",
        cef_types=["url", "domain"],
        example_values=["https://soar.zendesk.com/api/v2/tickets/1189.json"],
    )
    subject: str | None = OutputField(column_name="SUBJECT", example_values=["test"])
    status: str = OutputField(column_name="STATUS", example_values=["new"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2018-11-20T13:41:01Z"]
    )
    assignee_id_name: str | None = OutputField(column_name="ASSIGNEE")
    description: str = OutputField(column_name="DESCRIPTION", example_values=["QA"])
    requester_id_name: str | None = OutputField(
        column_name="REQUESTER", example_values=["Herman Edwards"]
    )

    allow_attachments: bool
    allow_channelback: bool = OutputField(example_values=[False, True])
    assignee_id: int | None
    custom_fields: list[CustomFieldsOutput]
    due_at: str | None
    external_id: str | None
    fields: list[FieldsOutput]
    forum_topic_id: int | None
    from_messaging_channel: bool
    group_id: int | None = OutputField(example_values=[28493297])
    has_incidents: bool = OutputField(example_values=[False, True])
    is_public: bool
    organization_id: int | None = OutputField(example_values=[3853131587])
    priority: str | None
    problem_id: int | None
    raw_subject: str = OutputField(example_values=["test"])
    requester_id: int | None = OutputField(example_values=[5980690157])
    satisfaction_probability: float | None
    submitter_id: int | None = OutputField(example_values=[5980690157])
    submitter_id_name: str | None = OutputField(example_values=["Herman Edwards"])
    tags: list[str]
    ticket_form_id: int | None = OutputField(example_values=[181987])
    type: str | None
    updated_at: str = OutputField(example_values=["2018-11-20T13:41:01Z"])
    via: ViaOutput


class CreateTicketSummary(ActionOutput):
    created_ticket_id: int


def create_ticket(params: CreateTicketParams, soar: SOARClient, asset: Asset):
    ticket = {"subject": params.subject, "comment": {"body": params.description}}
    if params.fields:
        try:
            fields = json.loads(params.fields)
        except (TypeError, ValueError) as exc:
            raise ActionFailure("fields must contain valid JSON") from exc
        if not isinstance(fields, dict):
            raise ActionFailure("fields must contain a JSON object")
        if fields.get("custom_fields"):
            fields["custom_fields"] = resolve_custom_fields(
                asset, fields["custom_fields"]
            )
        if fields:
            ticket.update(fields)
    payload = zendesk_request(asset, "POST", "/tickets.json", data={"ticket": ticket})
    created_ticket = payload["ticket"]
    ticket_id = int(created_ticket["id"])
    summary = CreateTicketSummary(created_ticket_id=ticket_id)
    soar.set_summary(summary)
    try:
        enrich_ticket_user_names(asset, [created_ticket])
    except ActionFailure:
        # Return the ticket and summary because Zendesk already created it.
        result = ActionResult(
            status=False,
            message=f"Zendesk created ticket {ticket_id}, but user-name enrichment failed.",
            param=params.model_dump(),
        )
        result.add_data(created_ticket)
        result.set_summary(summary.model_dump())
        return result
    return CreateTicketOutput(**created_ticket)
