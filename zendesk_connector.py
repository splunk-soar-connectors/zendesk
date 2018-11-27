# File: zendesk_connector.py
# Copyright (c) 2016-2018 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
""" Code that implements calls made to the zendesk systems device"""

# Phantom imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# THIS Connector imports
from zendesk_consts import *

import requests
import simplejson as json


class ZendeskConnector(BaseConnector):

    # actions supported by this script
    ACTION_ID_LIST_TICKETS = "list_tickets"
    ACTION_ID_CREATE_TICKET = "create_ticket"
    ACTION_ID_GET_TICKET = "get_ticket"
    ACTION_ID_UPDATE_TICKET = "update_ticket"
    ACTION_ID_RUN_QUERY = "run_query"

    def __init__(self):
        """ """

        self.__id_to_name = {}

        # Call the BaseConnectors init first
        super(ZendeskConnector, self).__init__()

    def initialize(self):
        """ Called once for every action, all member initializations occur here"""

        config = self.get_config()

        # Get the Base URL from the asset config and so some cleanup
        self._base_url = config[ZENDESK_JSON_DEVICE_URL]
        if (self._base_url.endswith('/')):
            self._base_url = self._base_url[:-1]

        # The host member extacts the host from the URL, is used in creating status messages
        self._host = self._base_url[self._base_url.find('//') + 2:]

        # The headers, initialize them here once and use them for all other REST calls
        self._headers = {'Accept': 'application/json'}

        # The common part after the base url, but before the specific endpoint
        # Intiliazed here and used on every REST endpoint calls
        self._api_uri = '/api/v2'

        password = config.get(phantom.APP_JSON_PASSWORD)
        api_token = config.get(ZENDESK_JSON_API_TOKEN)

        if ((not password) and (not api_token)):
            return self.set_status(phantom.APP_ERROR, "Please specify one of either 'Password' or 'API Token'")

        self._username = config[phantom.APP_JSON_USERNAME]

        self._auth_method = "password"

        if (password):
            self._key = password
        else:
            self._key = api_token
            self._username += '/token'
            self._auth_method = "api token"

        return phantom.APP_SUCCESS

    def _get_error_details(self, resp_json):
        """ Function that parses the error json recieved from the device and placed into a json"""

        error_details = {"message": "Not Found", "detail": "Not supplied"}

        if (not resp_json):
            return error_details

        error_info = resp_json.get("error")

        if (not error_info):
            return error_details

        if ('message' in error_info):
            error_details['message'] = error_info['message']

        if ('detail' in error_info):
            error_details['detail'] = error_info['detail']

        return error_details

    def _make_rest_call(self, endpoint, action_result, headers={}, params=None, data=None, method="get"):
        """ Function that makes the REST call to the device, generic function that can be called from various action handlers"""

        # Create the headers
        headers.update(self._headers)

        if (method in ['put', 'post']):
            headers.update({'Content-Type': 'application/json'})

        resp_json = None

        # get or post or put, whatever the caller asked us to use, if not specified the default will be 'get'
        request_func = getattr(requests, method)

        # handle the error in case the caller specified a non-existant method
        if (not request_func):
            action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_API_UNSUPPORTED_METHOD, method=method)

        self.save_progress('Using {0} for authentication'.format(self._auth_method))

        # Make the call
        try:
            r = request_func(self._base_url + self._api_uri + endpoint,  # The complete url is made up of the base_url, the api url and the endpiont
                    auth=(self._username, self._key),  # The authentication method, currently set to simple base authentication
                    data=json.dumps(data) if data else None,  # the data, converted to json string format if present, else just set to None
                    headers=headers,  # The headers to send in the HTTP call
                    verify=True,  # cert verification should be true
                    params=params)  # uri parameters if any
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_SERVER_CONNECTION, e), resp_json)

        # self.debug_print('REST url: {0}'.format(r.url))

        # Try a json parse, since most REST API's give back the data in json, if the device does not return JSONs, then need to implement parsing them some other manner
        try:
            resp_json = r.json()
        except Exception as e:
            # r.text is guaranteed to be NON None, it will be empty, but not None
            try:
                msg_string = ZENDESK_ERR_JSON_PARSE.format(raw_text=r.text.encode('utf-8'))
            except:
                msg_string = "Unable to parse response as a Json"
            if len(msg_string) > 500:
                msg_string = 'Error while parsing the response'
            return (action_result.set_status(phantom.APP_ERROR, msg_string, e), resp_json)

        # Handle any special HTTP error codes here, many devices return an HTTP error code like 204. The requests module treats these as error,
        # so handle them here before anything else, uncomment the following lines in such cases
        # if (r.status_code == 201):
        #     return (phantom.APP_SUCCESS, resp_json)

        # Handle/process any errors that we get back from the device
        if (200 <= r.status_code <= 399):
            # Success
            return (phantom.APP_SUCCESS, resp_json)

        # Failure
        action_result.add_data(resp_json)

        details = json.dumps(resp_json).replace('{', '').replace('}', '')

        return (action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_FROM_SERVER.format(status=r.status_code, detail=details)), resp_json)

    def _test_connectivity(self, param):
        """ Function that handles the test connectivity action, it is much simpler than other action handlers."""

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # set the endpoint
        endpoint = '/tickets/recent.json'

        params = {'per_page': 1}

        # Action result to represent the call
        action_result = ActionResult()

        # Progress message, since it is test connectivity, it pays to be verbose
        self.save_progress(ZENDESK_MSG_GET_INCIDENT_TEST)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result, params=params)

        # Process errors
        if (phantom.is_fail(ret_val)):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())

            # Set the status of the complete connector result
            self.set_status(phantom.APP_ERROR, action_result.get_message())

            # Append the message to display
            self.append_to_message(ZENDESK_ERR_CONNECTIVITY_TEST)

            # return error
            return phantom.APP_ERROR

        # Set the status of the connector result
        return self.set_status_save_progress(phantom.APP_SUCCESS, ZENDESK_SUCC_CONNECTIVITY_TEST)

    def _get_fields(self, param, action_result):
        """ Validates the field parameter that is a json, created a function to make the caller code cleaner"""

        fields = param.get(ZENDESK_JSON_FIELDS)

        # fields is an optional field
        if (not fields):
            return (phantom.APP_SUCCESS, None)

        # we take in as a dictionary string, first try to load it as is
        try:
            fields = json.loads(fields)
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_FIELDS_JSON_PARSE, e), None)

        return (phantom.APP_SUCCESS, fields)

    def _add_names_to_ids(self, ticket):
        """ Function parses the ticket and adds names to all the ids present in it """

        user_id_keys = ['submitter_id', 'assignee_id', 'requester_id']

        for user_id_key in user_id_keys:

            user_id = ticket[user_id_key]

            key_name = '{0}_name'.format(user_id_key)

            user_name = self.__id_to_name.get(user_id)

            if (user_name):
                ticket[key_name] = user_name
                continue

            user_details_ar = ActionResult()

            endpoint = '/users/{0}.json'.format(user_id)

            # Make the rest call
            ret_val, response = self._make_rest_call(endpoint, user_details_ar)
            if (phantom.is_fail(ret_val)):
                continue

            user = response.get('user')
            if (not user):
                continue

            ticket[key_name] = user.get('name')
            if (ticket[key_name]):
                self.__id_to_name[user_id] = ticket[key_name]

        return

    def _create_ticket(self, param):
        """ Action handler for the 'create ticket' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Set the endpoint
        endpoint = '/tickets.json'

        ticket = {'subject': param[ZENDESK_JSON_SUBJECT], 'comment': {'body': param[ZENDESK_JSON_DESCRIPTION]}}

        # Parse and set the fields parameter, it is optional
        ret_val, fields = self._get_fields(param, action_result)

        # Process error
        if (phantom.is_fail(ret_val)):
            return action_result.get_status()

        # If 'fields' is specified, use it i.e. add it to the data that will be sent off
        # If 'fields' is not a proper json i.e. some normal string or integer, it will throw an exception
        try:
            if (fields):
                ticket.update(fields)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_FIELDS_JSON_PARSE, e)

        data = {'ticket': ticket}

        # Make the rest call
        ret_val, response = self._make_rest_call(endpoint, action_result, data=data, method="post")

        # Process/parse the errors encountered while making the REST call.
        if (phantom.is_fail(ret_val)):
            self.debug_print(action_result.get_message())
            self.set_status(phantom.APP_ERROR, action_result.get_message())
            return phantom.APP_ERROR

        # parse the response from the REST call, this is very specific to the device being managed
        created_ticket = response['ticket']

        # Set the summary in the action_result
        action_result.set_summary({ZENDESK_JSON_NEW_TICKET_ID: created_ticket['id']})

        self._add_names_to_ids(created_ticket)

        # set the data
        action_result.add_data(created_ticket)

        # set the status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _update_ticket(self, param):
        """ Action handler for the 'update ticket' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # set the endpoint
        endpoint = '/tickets/{0}.json'.format(param[ZENDESK_JSON_TICKET_ID])

        # Parse and set the fields parameter, it is required for this action
        ret_val, fields = self._get_fields(param, action_result)

        # Process error
        if (phantom.is_fail(ret_val)):
            return action_result.get_status()

        # If 'fields' is not specified, it is an error
        if (not fields):
            return action_result.set_status(phantom.APP_ERROR, ZENDESK_ERR_EMPTY_FIELDS)

        data = {'ticket': fields}

        # Make the REST CAll
        ret_val, response = self._make_rest_call(endpoint, action_result, data=data, method="put")

        # Process the error
        if (phantom.is_fail(ret_val)):
            self.debug_print(action_result.get_message())
            return action_result.get_status()

        # Get the result
        ticket = response.get('ticket')

        self._add_names_to_ids(ticket)

        # Set the summary
        action_result.set_summary({ZENDESK_JSON_UPDATED_TICKET_ID: ticket['id']})

        # Add the data
        action_result.add_data(ticket)

        # Set the status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_ticket(self, param):
        """ Action handler for the 'get ticket' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # set the endpoint
        endpoint = '/tickets/{0}.json'.format(param[ZENDESK_JSON_TICKET_ID])

        # Make the rest call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        # Process the error
        if (phantom.is_fail(ret_val)):
            self.debug_print(action_result.get_message())
            self.set_status(phantom.APP_ERROR, action_result.get_message())
            return phantom.APP_ERROR

        # Process the return result
        ticket = response['ticket']

        self._add_names_to_ids(ticket)

        # Set the summary
        action_result.set_summary({ZENDESK_JSON_GOT_TICKET_ID: ticket['id']})

        # Add the data
        action_result.add_data(ticket)

        # Set the status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _list_tickets(self, param):
        """ Action handler for the 'list tickets' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Endpoint
        endpoint = '/tickets.json'

        params = {
                'per_page': param.get(ZENDESK_JSON_PER_PAGE, 100),
                'page': param.get(ZENDESK_JSON_PAGE, 1)
        }

        # Make the rest call
        ret_val, response = self._make_rest_call(endpoint, action_result, params=params)

        # Process errors
        if (phantom.is_fail(ret_val)):
            self.debug_print(action_result.get_message())
            self.set_status(phantom.APP_ERROR, action_result.get_message())
            return phantom.APP_ERROR

        # Process successfull response
        tickets = response['tickets']

        # Set the summary
        action_result.set_summary({ZENDESK_JSON_TOTAL_TICKETS: len(tickets)})

        # Add each ticket as a data
        for ticket in tickets:
            self._add_names_to_ids(ticket)
            action_result.add_data(ticket)

        # Set the Status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _run_query(self, param):
        """ Action handler for the 'run query' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Progress
        self.save_progress(ZENDESK_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Endpoint
        endpoint = '/search.json'

        query_type = 'ticket'

        # Parameters, I don't think these need to be url encoded
        request_params = {'query': 'type:{0} {1}'.format(query_type, param[ZENDESK_JSON_QUERY])}

        request_params.update({
                'per_page': param.get(ZENDESK_JSON_PER_PAGE, 100),
                'page': param.get(ZENDESK_JSON_PAGE, 1)
        })

        # Make the rest call
        ret_val, response = self._make_rest_call(endpoint, action_result, params=request_params)

        # Process errors
        if (phantom.is_fail(ret_val)):
            self.debug_print(action_result.get_message())
            self.set_status(phantom.APP_ERROR, action_result.get_message())
            return phantom.APP_ERROR

        # Process successfull response
        tickets = response.get('results', [])

        # Set the summary
        action_result.set_summary({ZENDESK_JSON_TOTAL_TICKETS: response.get('count'),
            ZENDESK_JSON_RETURNED_TICKETS: len(tickets)})

        for ticket in tickets:

            self._add_names_to_ids(ticket)
            # Add as data to the action result
            action_result.add_data(ticket)

        # Set the Status
        return action_result.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        """Function that handles all the actions"""

        # Get the action that we are supposed to carry out, set it in the connection result object
        action = self.get_action_identifier()

        # Intialize it to success
        ret_val = phantom.APP_SUCCESS

        # Bunch if if..elif to process actions
        if (action == self.ACTION_ID_CREATE_TICKET):
            ret_val = self._create_ticket(param)
        elif (action == self.ACTION_ID_LIST_TICKETS):
            ret_val = self._list_tickets(param)
        elif (action == self.ACTION_ID_GET_TICKET):
            ret_val = self._get_ticket(param)
        elif (action == self.ACTION_ID_UPDATE_TICKET):
            ret_val = self._update_ticket(param)
        elif (action == self.ACTION_ID_RUN_QUERY):
            ret_val = self._run_query(param)
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            ret_val = self._test_connectivity(param)

        return ret_val


if __name__ == '__main__':
    """ Code that is executed when run in standalone debug mode
    for .e.g:
    python2.7 ./zendesk_connector.py /tmp/zendesk_test_create_ticket.json
        """

    # Imports
    import sys
    import pudb

    # Breakpoint at runtime
    pudb.set_trace()

    # The first param is the input json file
    with open(sys.argv[1]) as f:

        # Load the input json file
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=' ' * 4))

        # Create the connector class object
        connector = ZendeskConnector()

        # Se the member vars
        connector.print_progress_message = True

        # Call BaseConnector::_handle_action(...) to kickoff action handling.
        ret_val = connector._handle_action(json.dumps(in_json), None)

        # Dump the return value
        print ret_val

    exit(0)
