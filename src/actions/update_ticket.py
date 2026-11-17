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
"""Zendesk update_ticket action."""

import json

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.params import Param, Params
from soar_sdk.exceptions import ActionFailure

from ..app import Asset, app
from ..helper import (
    enrich_ticket_user_names,
    request as zendesk_request,
    resolve_custom_fields,
    ticket_output,
)


class UpdateTicketParams(Params):
    id: str = Param(
        description="Ticket ID", primary=True, cef_types=["zendesk ticket id"]
    )
    fields: str = Param(description="Json containing field values")


class CustomFieldsOutput(PermissiveActionOutput):
    id: float = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["custom field value"])


class FieldsOutput(PermissiveActionOutput):
    id: float = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["test field value"])


class SourceOutput(ActionOutput):
    rel: str


class ViaOutput(ActionOutput):
    channel: str = OutputField(example_values=["api"])
    source: SourceOutput


class UpdateTicketOutput(PermissiveActionOutput):
    id: float = OutputField(
        column_name="ID", cef_types=["zendesk ticket id"], example_values=[9]
    )
    url: str = OutputField(
        column_name="URL",
        cef_types=["url", "domain"],
        example_values=["https://soar.zendesk.com/api/v2/tickets/9.json"],
    )
    subject: str = OutputField(column_name="SUBJECT", example_values=["Zeus"])
    status: str = OutputField(column_name="STATUS", example_values=["open"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2016-05-18T22:32:57Z"]
    )
    assignee_id_name: str = OutputField(
        column_name="ASSIGNEE", example_values=["Herman Edwards"]
    )
    description: str = OutputField(
        column_name="DESCRIPTION", example_values=["Remediate quickly"]
    )
    requester_id_name: str = OutputField(
        column_name="REQUESTER", example_values=["Herman Edwards"]
    )

    allow_attachments: bool
    allow_channelback: bool = OutputField(example_values=[False, True])
    assignee_id: float = OutputField(example_values=[5980690157])
    brand_id: float = OutputField(example_values=[1103787])
    custom_fields: list[CustomFieldsOutput]
    due_at: str
    external_id: str
    fields: list[FieldsOutput]
    forum_topic_id: str
    from_messaging_channel: bool
    group_id: float = OutputField(example_values=[28493297])
    has_incidents: bool = OutputField(example_values=[False, True])
    is_public: bool
    organization_id: float = OutputField(example_values=[3853131587])
    priority: str
    problem_id: str
    raw_subject: str = OutputField(example_values=["Zeus"])
    recipient: str
    requester_id: float = OutputField(example_values=[5980690157])
    satisfaction_probability: str
    satisfaction_rating: str
    submitter_id: float = OutputField(example_values=[5980690157])
    submitter_id_name: str = OutputField(example_values=["Herman Edwards"])
    tags: str
    ticket_form_id: str
    type: str
    updated_at: str = OutputField(example_values=["2018-11-16T10:38:57Z"])
    via: ViaOutput


class UpdateTicketSummary(ActionOutput):
    updated_ticket_id: int
    total_tickets: int


@app.action(
    description="Update ticket information",
    action_type="generic",
    read_only=False,
    render_as="table",
    summary_type=UpdateTicketSummary,
    verbose='Update an already existing ticket with the values that are specified in the \'fields\' parameter. The user has to know the key names to set in this parameter. Please refer to the Zendesk Core API, Tickets section to learn about the fields that can be used to update or create tickets.<br>The JSON that is specified in the \'fields\' parameter should have the keys and values specified in double quotes string format, except in case of boolean values, which should be either <i>true</i> or <i>false</i>.<br>Some examples: <ul><li>To close a ticket: {\\"subject\\": \\"Zeus, multiple action need to be taken\\", \\"status\\": \\"solved\\"}</li><li>To add a comment: {\\"status\\": \\"open\\", \\"comment\\": { \\"body\\": \\"The smoke is very colorful.\\", \\"author_id\\": 1 }}</li><li>To update custom fields value: {\\"custom_fields\\": [{\\"Test Field\\": \\"test field value\\"}, {\\"custom test field\\": \\"custom test field value\\"}]}</li></ul>If you want to add <b>double quote(\\")</b> or <b>backslash(\\)</b> in custom fields, use the <b>escape(\\)</b> character followed by double quote or backslash, check the following examples,<br><ul><li>To add double quote or backslash in custom field values: {\\"custom_fields\\": [{\\"Test Field\\": \\"test \\\\"field\\\\" value\\"}, {\\"custom test field\\": \\"custom \\\\test\\\\ field value\\"}]}</li><li>To add double quote or backslash in custom field keys: {\\"custom_fields\\": [{\\"Test \\\\"Name\\\\" Field\\": \\"test field value\\"}, {\\"custom \\\\test\\\\ field\\": \\"custom test field value\\"}]}</li></ul>',
)
def update_ticket(
    params: UpdateTicketParams, soar: SOARClient, asset: Asset
) -> UpdateTicketOutput:
    if not params.id.isascii() or not params.id.isdecimal() or int(params.id) < 1:
        raise ActionFailure("Ticket ID must be a positive integer")
    try:
        fields = json.loads(params.fields)
    except (TypeError, ValueError) as exc:
        raise ActionFailure("fields must contain valid JSON") from exc
    if not isinstance(fields, dict) or not fields:
        raise ActionFailure("fields must be a non-empty JSON object")
    if fields.get("custom_fields"):
        fields["custom_fields"] = resolve_custom_fields(asset, fields["custom_fields"])
    payload = zendesk_request(
        asset,
        "PUT",
        f"/tickets/{params.id}.json",
        data={"ticket": fields},
    )
    ticket = payload["ticket"]
    enrich_ticket_user_names(asset, [ticket])
    soar.set_summary(
        UpdateTicketSummary(updated_ticket_id=int(ticket["id"]), total_tickets=1)
    )
    soar.set_message(f"Updated ticket id: {ticket['id']}")
    return ticket_output(UpdateTicketOutput, ticket)
