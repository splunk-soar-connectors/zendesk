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
"""Zendesk action registrations."""

from soar_sdk.app import App

from .create_ticket import CreateTicketOutput, CreateTicketSummary, create_ticket
from .get_ticket import GetTicketSummary, get_ticket
from .list_tickets import ListTicketsSummary, list_tickets
from .make_request import make_request
from .run_query import RunQuerySummary, run_query
from .update_ticket import UpdateTicketSummary, update_ticket


def register_actions(app: App) -> None:
    """Register the Zendesk handlers on the supplied app instance."""
    app.register_action(
        create_ticket,
        description="Create a Ticket",
        action_type="generic",
        read_only=False,
        render_as="table",
        output_class=CreateTicketOutput,
        summary_type=CreateTicketSummary,
        verbose='If you want to assign the value to custom fields, use the following format in \'fields\' parameter<br>{\\"custom_fields\\": [{\\"Test Field\\": \\"test field value\\"}, {\\"custom test field\\": \\"custom test field value\\"}]}<br>If you want to add <b>double quote(\\")</b> or <b>backslash(\\)</b> in custom fields, use the <b>escape(\\)</b> character followed by double quote or backslash, check the following examples,<br><ul><li>To add double quote or backslash in custom field values: {\\"custom_fields\\": [{\\"Test Field\\": \\"test \\\\"field\\\\" value\\"}, {\\"custom test field\\": \\"custom \\\\test\\\\ field value\\"}]}</li><li>To add double quote or backslash in custom field keys: {\\"custom_fields\\": [{\\"Test \\\\"Name\\\\" Field\\": \\"test field value\\"}, {\\"custom \\\\test\\\\ field\\": \\"custom test field value\\"}]}</li></ul>',
    )
    app.register_action(
        get_ticket,
        description="Get ticket information",
        action_type="generic",
        read_only=True,
        render_as="table",
        summary_type=GetTicketSummary,
    )
    app.register_action(
        list_tickets,
        description="Get a list of Tickets",
        action_type="generic",
        read_only=True,
        render_as="table",
        summary_type=ListTicketsSummary,
    )
    app.make_request()(make_request)
    app.register_action(
        run_query,
        description="Search tickets",
        action_type="investigate",
        read_only=True,
        render_as="table",
        summary_type=RunQuerySummary,
        verbose="A <b>ticket</b> type query is executed on Zendesk.",
    )
    app.register_action(
        update_ticket,
        description="Update ticket information",
        action_type="generic",
        read_only=False,
        render_as="table",
        summary_type=UpdateTicketSummary,
        verbose='Update an already existing ticket with the values that are specified in the \'fields\' parameter. The user has to know the key names to set in this parameter. Please refer to the Zendesk Core API, Tickets section to learn about the fields that can be used to update or create tickets.<br>The JSON that is specified in the \'fields\' parameter should have the keys and values specified in double quotes string format, except in case of boolean values, which should be either <i>true</i> or <i>false</i>.<br>Some examples: <ul><li>To close a ticket: {\\"subject\\": \\"Zeus, multiple action need to be taken\\", \\"status\\": \\"solved\\"}</li><li>To add a comment: {\\"status\\": \\"open\\", \\"comment\\": { \\"body\\": \\"The smoke is very colorful.\\", \\"author_id\\": 1 }}</li><li>To update custom fields value: {\\"custom_fields\\": [{\\"Test Field\\": \\"test field value\\"}, {\\"custom test field\\": \\"custom test field value\\"}]}</li></ul>If you want to add <b>double quote(\\")</b> or <b>backslash(\\)</b> in custom fields, use the <b>escape(\\)</b> character followed by double quote or backslash, check the following examples,<br><ul><li>To add double quote or backslash in custom field values: {\\"custom_fields\\": [{\\"Test Field\\": \\"test \\\\"field\\\\" value\\"}, {\\"custom test field\\": \\"custom \\\\test\\\\ field value\\"}]}</li><li>To add double quote or backslash in custom field keys: {\\"custom_fields\\": [{\\"Test \\\\"Name\\\\" Field\\": \\"test field value\\"}, {\\"custom \\\\test\\\\ field\\": \\"custom test field value\\"}]}</li></ul>',
    )


__all__ = [
    "create_ticket",
    "get_ticket",
    "list_tickets",
    "make_request",
    "register_actions",
    "run_query",
    "update_ticket",
]
