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
"""Zendesk list_tickets action."""

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
from ..helper import enrich_ticket_user_names, request as zendesk_request


class ListTicketsParams(Params):
    max_results_per_page: int | None = Param(
        description="Max number of tickets to return per page", default=100
    )
    page_number: int | None = Param(description="The page number to get", default=1)


class CustomFieldsOutput(PermissiveActionOutput):
    """Preserve values whose types vary by Zendesk custom-field configuration."""

    id: int = OutputField(example_values=[360011869194])


class FieldsOutput(PermissiveActionOutput):
    """Preserve values whose types vary by Zendesk custom-field configuration."""

    id: int = OutputField(example_values=[360011869194])


class SourceOutput(ActionOutput):
    rel: str | None


class ViaOutput(ActionOutput):
    channel: str = OutputField(example_values=["web"])
    source: SourceOutput | None


class ListTicketsOutput(PermissiveActionOutput):
    """Preserve raw brand_id, recipient, and satisfaction_rating values.

    Zendesk returns multiple types for these fields, which the SOAR manifest
    cannot describe.
    """

    id: int = OutputField(
        column_name="ID",
        cef_types=["zendesk ticket id"],
        example_values=[7],
    )
    url: str = OutputField(
        column_name="URL",
        cef_types=["url", "domain"],
        example_values=["https://soar.zendesk.com/api/v2/tickets/7.json"],
    )
    subject: str | None = OutputField(
        column_name="SUBJECT", example_values=["<b>bold?</b>not bold?"]
    )
    status: str = OutputField(column_name="STATUS", example_values=["open"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2016-05-17T22:16:39Z"]
    )
    assignee_id_name: str | None = OutputField(
        column_name="ASSIGNEE", example_values=["Herman Edwards"]
    )
    description: str = OutputField(
        column_name="DESCRIPTION", example_values=["㯙㯜㯙㯟"]
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
    raw_subject: str = OutputField(example_values=["<b>bold?</b>not bold?"])
    requester_id: int | None = OutputField(example_values=[5980690157])
    satisfaction_probability: float | None
    submitter_id: int | None = OutputField(example_values=[5980690157])
    submitter_id_name: str | None = OutputField(example_values=["Herman Edwards"])
    tags: list[str]
    ticket_form_id: int | None
    type: str | None
    updated_at: str = OutputField(example_values=["2016-05-20T00:50:34Z"])
    via: ViaOutput


class ListTicketsSummary(ActionOutput):
    total_tickets: int


def list_tickets(
    params: ListTicketsParams, soar: SOARClient, asset: Asset
) -> list[ListTicketsOutput]:
    payload = zendesk_request(
        asset,
        "GET",
        "/tickets.json",
        params={
            "per_page": params.max_results_per_page
            if params.max_results_per_page is not None
            else 100,
            "page": params.page_number if params.page_number is not None else 1,
        },
    )
    tickets = payload["tickets"]
    summary = ListTicketsSummary(total_tickets=len(tickets))
    soar.set_summary(summary)
    outputs = []
    partial_data = []
    name_cache = {}
    for ticket in tickets:
        try:
            enrich_ticket_user_names(asset, [ticket], name_cache)
            outputs.append(ListTicketsOutput(**ticket))
            partial_data.append(dict(ticket))
        except ActionFailure as error:
            if not partial_data:
                raise
            # Preserve successful rows on a later failure, matching legacy behavior.
            failed_result = ActionResult(
                status=False,
                message=str(error),
                param=params.model_dump(),
            )
            for row in partial_data:
                failed_result.add_data(row)
            failed_result.set_summary(summary.model_dump())
            return failed_result
    return outputs
