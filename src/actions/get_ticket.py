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
"""Zendesk get_ticket action."""

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from ..asset import Asset
from ..helper import enrich_ticket_user_names, request as zendesk_request


class GetTicketParams(Params):
    id: str = Param(
        description="Ticket ID", primary=True, cef_types=["zendesk ticket id"]
    )


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


class GetTicketOutput(PermissiveActionOutput):
    """Preserve raw brand_id, recipient, and satisfaction_rating values.

    Zendesk returns multiple types for these fields, which the SOAR manifest
    cannot describe.
    """

    id: int = OutputField(
        column_name="ID", cef_types=["zendesk ticket id"], example_values=[12]
    )
    url: str = OutputField(
        column_name="URL",
        cef_types=["url", "domain"],
        example_values=["https://soar.zendesk.com/api/v2/tickets/12.json"],
    )
    subject: str | None = OutputField(
        column_name="SUBJECT", example_values=["Zeus detections"]
    )
    status: str = OutputField(column_name="STATUS", example_values=["open"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2016-05-19T00:15:53Z"]
    )
    assignee_id_name: str | None = OutputField(
        column_name="ASSIGNEE", example_values=["Herman Edwards"]
    )
    description: str = OutputField(
        column_name="DESCRIPTION", example_values=["Remediate quickly"]
    )
    requester_id_name: str | None = OutputField(
        column_name="REQUESTER", example_values=["Herman Edwards"]
    )

    allow_attachments: bool
    allow_channelback: bool = OutputField(example_values=[False, True])
    assignee_id: int | None = OutputField(example_values=[5980690157])
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
    raw_subject: str = OutputField(example_values=["Zeus detections"])
    requester_id: int | None = OutputField(example_values=[5980690157])
    satisfaction_probability: float | None
    submitter_id: int | None = OutputField(example_values=[5980690157])
    submitter_id_name: str | None = OutputField(example_values=["Herman Edwards"])
    tags: list[str]
    ticket_form_id: int | None
    type: str | None
    updated_at: str = OutputField(example_values=["2016-05-19T00:15:53Z"])
    via: ViaOutput


class GetTicketSummary(ActionOutput):
    queried_ticket_id: int
    total_tickets: int


def get_ticket(
    params: GetTicketParams, soar: SOARClient, asset: Asset
) -> GetTicketOutput:
    if not params.id.isascii() or not params.id.isdecimal() or int(params.id) < 1:
        raise ActionFailure("Ticket ID must be a positive integer")
    payload = zendesk_request(asset, "GET", f"/tickets/{params.id}.json")
    if not payload.get("ticket"):
        raise ActionFailure("No data found")
    ticket = payload["ticket"]
    enrich_ticket_user_names(asset, [ticket])
    soar.set_summary(
        GetTicketSummary(queried_ticket_id=int(ticket["id"]), total_tickets=1)
    )
    return GetTicketOutput(**ticket)
