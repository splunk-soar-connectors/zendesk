**Unreleased**

* Migrated the Zendesk connector to the Splunk SOAR SDK.
* The minimum supported Splunk SOAR version is now 7.0.0.
* Added the `make request` action for authenticated requests to Zendesk API endpoints.
* If name enrichment fails after ticket creation, the created ticket ID is now available in `action_result.message`, replacing the summary path `action_result.summary.created_ticket_id`.
