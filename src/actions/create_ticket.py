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
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..app import Asset, app
from ..helper import (
    enrich_ticket_user_names,
    request as zendesk_request,
    resolve_custom_fields,
    ticket_output,
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


@app.action(
    description="Create a Ticket",
    action_type="generic",
    read_only=False,
    render_as="table",
    summary_type=CreateTicketSummary,
    verbose='If you want to assign the value to custom fields, use the following format in \'fields\' parameter<br>{\\"custom_fields\\": [{\\"Test Field\\": \\"test field value\\"}, {\\"custom test field\\": \\"custom test field value\\"}]}<br>If you want to add <b>double quote(\\")</b> or <b>backslash(\\)</b> in custom fields, use the <b>escape(\\)</b> character followed by double quote or backslash, check the following examples,<br><ul><li>To add double quote or backslash in custom field values: {\\"custom_fields\\": [{\\"Test Field\\": \\"test \\\\"field\\\\" value\\"}, {\\"custom test field\\": \\"custom \\\\test\\\\ field value\\"}]}</li><li>To add double quote or backslash in custom field keys: {\\"custom_fields\\": [{\\"Test \\\\"Name\\\\" Field\\": \\"test field value\\"}, {\\"custom \\\\test\\\\ field\\": \\"custom test field value\\"}]}</li></ul>',
)
def create_ticket(
    params: CreateTicketParams, soar: SOARClient, asset: Asset
) -> CreateTicketOutput:
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
    soar.set_summary(CreateTicketSummary(created_ticket_id=int(created_ticket["id"])))
    enrich_ticket_user_names(asset, [created_ticket])
    return ticket_output(CreateTicketOutput, created_ticket)
