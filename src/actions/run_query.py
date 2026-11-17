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
"""Zendesk run_query action."""

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


class RunQueryParams(Params):
    query: str = Param(description="Query to search tickets")
    max_results_per_page: float | None = Param(
        description="Max number of tickets to return per page", default=100
    )
    page_number: float | None = Param(description="The page number to get", default=1)


class CustomFieldsOutput(PermissiveActionOutput):
    id: float = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["test field value"])


class FieldsOutput(PermissiveActionOutput):
    id: float = OutputField(example_values=[360011869194])
    value: str = OutputField(example_values=["test field value"])


class FromOutput(ActionOutput):
    address: str = OutputField(example_values=["testuser@gmail.com"])
    name: str = OutputField(example_values=["Maddie"])


class ToOutput(ActionOutput):
    address: str = OutputField(example_values=["support@soar.zendesk.com"])
    name: str = OutputField(example_values=["SOAR Cyber"])


class SourceOutput(ActionOutput):
    from_: FromOutput
    rel: str
    to: ToOutput


class ViaOutput(ActionOutput):
    channel: str = OutputField(example_values=["web"])
    source: SourceOutput


class RunQueryOutput(PermissiveActionOutput):
    id: float = OutputField(
        column_name="ID", cef_types=["zendesk ticket id"], example_values=[1188]
    )
    url: str = OutputField(
        column_name="URL",
        cef_types=["url", "domain"],
        example_values=["https://soar.zendesk.com/api/v2/tickets/1188.json"],
    )
    subject: str = OutputField(column_name="SUBJECT", example_values=["moshah ticket"])
    status: str = OutputField(column_name="STATUS", example_values=["open"])
    created_at: str = OutputField(
        column_name="CREATED AT", example_values=["2018-11-20T10:09:01Z"]
    )
    assignee_id_name: str = OutputField(
        column_name="ASSIGNEE", example_values=["Herman Edwards"]
    )
    description: str = OutputField(
        column_name="DESCRIPTION", example_values=["ticket for moshah"]
    )
    requester_id_name: str = OutputField(
        column_name="REQUESTER", example_values=["MOSHAH"]
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
    organization_id: float
    priority: str
    problem_id: str
    raw_subject: str = OutputField(example_values=["moshah ticket"])
    recipient: str
    requester_id: float = OutputField(example_values=[369385135314])
    result_type: str = OutputField(example_values=["ticket"])
    satisfaction_probability: str
    satisfaction_rating: str
    submitter_id: float = OutputField(example_values=[5980690157])
    submitter_id_name: str = OutputField(example_values=["Herman Edwards"])
    tags: str
    ticket_form_id: float = OutputField(example_values=[181987])
    type: str
    updated_at: str = OutputField(example_values=["2018-11-20T12:08:58Z"])
    via: ViaOutput


class RunQuerySummary(ActionOutput):
    total_tickets: int
    returned_tickets: int


@app.action(
    description="Search tickets",
    action_type="investigate",
    render_as="table",
    summary_type=RunQuerySummary,
    verbose="A <b>ticket</b> type query is executed on Zendesk.",
)
def run_query(
    params: RunQueryParams, soar: SOARClient, asset: Asset
) -> list[RunQueryOutput]:
    payload = zendesk_request(
        asset,
        "GET",
        "/search.json",
        params={
            "query": f"type:ticket {params.query}",
            "per_page": params.max_results_per_page
            if params.max_results_per_page is not None
            else 100,
            "page": params.page_number if params.page_number is not None else 1,
        },
    )
    tickets = payload.get("results", [])
    summary = RunQuerySummary(
        total_tickets=payload.get("count", 0),
        returned_tickets=len(tickets),
    )
    soar.set_summary(summary)
    outputs = []
    partial_data = []
    for ticket in tickets:
        try:
            enrich_ticket_user_names(asset, [ticket])
            outputs.append(ticket_output(RunQueryOutput, ticket))
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
