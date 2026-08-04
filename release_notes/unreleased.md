**Unreleased**

* Handle non-ticket search results and malformed ticket response shapes without unhandled exceptions.
* Require a new credential when an existing credential is used with a different Zendesk endpoint.
* Apply a 30-second timeout to Zendesk API requests so unresponsive endpoints return a connector error.
