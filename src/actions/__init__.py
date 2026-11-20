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

from .create_ticket import create_ticket
from .get_ticket import get_ticket
from .list_tickets import list_tickets
from .make_request import make_request
from .run_query import run_query
from .update_ticket import update_ticket

__all__ = [
    "create_ticket",
    "get_ticket",
    "list_tickets",
    "make_request",
    "run_query",
    "update_ticket",
]
