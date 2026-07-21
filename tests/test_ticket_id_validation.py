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
# pylint: disable=no-member
import importlib
import json
import sys
import types
import unittest


phantom = types.ModuleType("phantom")
phantom.APP_ERROR = -1
phantom.APP_SUCCESS = 0
phantom.APP_PROG_CONNECTING_TO_ELLIPSES = "Connecting to {0}"
phantom.is_fail = lambda status: status != phantom.APP_SUCCESS
phantom.app = types.SimpleNamespace(
    APP_ERROR=phantom.APP_ERROR,
    APP_PROG_CONNECTING_TO_ELLIPSES=phantom.APP_PROG_CONNECTING_TO_ELLIPSES,
    APP_SUCCESS=phantom.APP_SUCCESS,
    is_fail=phantom.is_fail,
)
sys.modules["phantom"] = phantom
sys.modules["phantom.app"] = phantom.app

action_result_module = types.ModuleType("phantom.action_result")
action_result_module.ActionResult = object
sys.modules["phantom.action_result"] = action_result_module

base_connector_module = types.ModuleType("phantom.base_connector")
base_connector_module.BaseConnector = object
sys.modules["phantom.base_connector"] = base_connector_module

sys.modules["requests"] = types.ModuleType("requests")
sys.modules["simplejson"] = json

zendesk_connector = importlib.import_module("zendesk_connector")


class ActionResult:
    def __init__(self, *_args):
        self.message = None

    def set_status(self, status, message):
        self.message = message
        return status

    def get_status(self):
        return phantom.APP_ERROR


zendesk_connector.ActionResult = ActionResult


class TicketIdValidationTest(unittest.TestCase):
    def setUp(self):
        self.connector = object.__new__(zendesk_connector.ZendeskConnector)

    def test_accepts_positive_numeric_ticket_id(self):
        status, endpoint = self.connector._get_ticket_endpoint({"id": "123"}, ActionResult())

        self.assertEqual(status, phantom.APP_SUCCESS)
        self.assertEqual(endpoint, "/tickets/123.json")

    def test_rejects_path_injection_ticket_id(self):
        action_result = ActionResult()
        status, endpoint = self.connector._get_ticket_endpoint({"id": "../users.json?"}, action_result)

        self.assertEqual(status, phantom.APP_ERROR)
        self.assertIsNone(endpoint)
        self.assertEqual(action_result.message, "Please provide a positive numeric ticket ID")

    def test_rejects_non_positive_ticket_ids(self):
        for ticket_id in ("0", "-1", "1.5", "", None):
            with self.subTest(ticket_id=ticket_id):
                status, endpoint = self.connector._get_ticket_endpoint({"id": ticket_id}, ActionResult())

                self.assertEqual(status, phantom.APP_ERROR)
                self.assertIsNone(endpoint)

    def test_handlers_reject_injected_ticket_ids_before_requesting(self):
        for handler_name in ("_get_ticket", "_update_ticket"):
            with self.subTest(handler_name=handler_name):
                action_result = ActionResult()
                self.connector._base_url = "https://example.zendesk.com"
                self.connector._host = "example.zendesk.com"
                self.connector.add_action_result = lambda _result: action_result
                self.connector.save_progress = lambda *_args, **_kwargs: None
                self.connector._make_rest_call = lambda *_args, **_kwargs: self.fail("unexpected REST request")

                status = getattr(self.connector, handler_name)({"id": "../users.json?"})

                self.assertEqual(status, phantom.APP_ERROR)
                self.assertEqual(action_result.message, "Please provide a positive numeric ticket ID")
