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
from soar_sdk.params import Param, Params

from ..app import Asset, app
from ..helper import enrich_ticket_user_names, request as zendesk_request, ticket_output


class ListTicketsParams(Params):
    max_results_per_page: int | None = Param(
        description="Max number of tickets to return per page", default=100
    )
    page_number: int | None = Param(description="The page number to get", default=1)


class CustomFieldsOutput(PermissiveActionOutput):
    id: int = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["custom field value"])


class FieldsOutput(PermissiveActionOutput):
    id: int = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["test field value"])


class SourceOutput(ActionOutput):
    rel: str


class ViaOutput(ActionOutput):
    channel: str = OutputField(example_values=["web"])
    source: SourceOutput


class ListTicketsOutput(PermissiveActionOutput):
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
    subject: str = OutputField(
        column_name="SUBJECT", example_values=["<b>bold?</b>not bold?"]
    )
    status: str = OutputField(column_name="STATUS", example_values=["open"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2016-05-17T22:16:39Z"]
    )
    assignee_id_name: str = OutputField(
        column_name="ASSIGNEE", example_values=["Herman Edwards"]
    )
    description: str = OutputField(
        column_name="DESCRIPTION", example_values=["㯙㯜㯙㯟"]
    )
    requester_id_name: str = OutputField(
        column_name="REQUESTER", example_values=["Herman Edwards"]
    )
    allow_attachments: bool
    allow_channelback: bool = OutputField(example_values=[False, True])
    assignee_id: int = OutputField(example_values=[5980690157])
    brand_id: int = OutputField(example_values=[1103787])
    custom_fields: list[CustomFieldsOutput]
    due_at: str
    external_id: str
    fields: list[FieldsOutput]
    forum_topic_id: int
    from_messaging_channel: bool
    group_id: int = OutputField(example_values=[28493297])
    has_incidents: bool = OutputField(example_values=[False, True])
    is_public: bool
    organization_id: int = OutputField(example_values=[3853131587])
    priority: str
    problem_id: int
    raw_subject: str = OutputField(example_values=["<b>bold?</b>not bold?"])
    recipient: str
    requester_id: int = OutputField(example_values=[5980690157])
    satisfaction_probability: str
    satisfaction_rating: str
    submitter_id: int = OutputField(example_values=[5980690157])
    submitter_id_name: str = OutputField(example_values=["Herman Edwards"])
    tags: list[str]
    ticket_form_id: int
    type: str
    updated_at: str = OutputField(example_values=["2016-05-20T00:50:34Z"])
    via: ViaOutput


class ListTicketsSummary(ActionOutput):
    total_tickets: int


@app.action(
    description="Get a list of Tickets",
    action_type="generic",
    render_as="table",
    summary_type=ListTicketsSummary,
)
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
    for ticket in tickets:
        try:
            enrich_ticket_user_names(asset, [ticket])
            outputs.append(ticket_output(ListTicketsOutput, ticket))
            partial_data.append(dict(ticket))
        except Exception as error:
            if not partial_data:
                raise
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
