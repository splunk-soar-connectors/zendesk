[comment]: # "Auto-generated SOAR connector documentation"
# Zendesk

Publisher: Splunk  
Connector Version: 2\.0\.4  
Product Vendor: Zendesk  
Product Name: Zendesk  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.1\.0  

This App allows for ticket management on Zendesk

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Zendesk asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**url** |  required  | string | Device URL including the port, e\.g\. https\://myzendesk\.enterprise\.com
**api\_token** |  optional  | password | API Token
**username** |  required  | string | Username
**password** |  optional  | password | Password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action runs a quick query on the device to check the connection and credentials  
[run query](#action-run-query) - Search tickets  
[list tickets](#action-list-tickets) - Get a list of Tickets  
[create ticket](#action-create-ticket) - Create a Ticket  
[get ticket](#action-get-ticket) - Get ticket information  
[update ticket](#action-update-ticket) - Update ticket information  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action runs a quick query on the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'run query'
Search tickets

Type: **investigate**  
Read only: **True**

A <b>ticket</b> type query is executed on Zendesk\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**query** |  required  | Query to search tickets | string | 
**max\_results\_per\_page** |  optional  | Max number of tickets to return per page | numeric | 
**page\_number** |  optional  | The page number to get | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.max\_results\_per\_page | numeric | 
action\_result\.parameter\.page\_number | numeric | 
action\_result\.parameter\.query | string | 
action\_result\.data\.\*\.allow\_attachments | boolean | 
action\_result\.data\.\*\.allow\_channelback | boolean | 
action\_result\.data\.\*\.assignee\_id | numeric | 
action\_result\.data\.\*\.assignee\_id\_name | string | 
action\_result\.data\.\*\.brand\_id | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.due\_at | string | 
action\_result\.data\.\*\.external\_id | string | 
action\_result\.data\.\*\.forum\_topic\_id | string | 
action\_result\.data\.\*\.group\_id | numeric | 
action\_result\.data\.\*\.has\_incidents | boolean | 
action\_result\.data\.\*\.id | numeric |  `zendesk ticket id` 
action\_result\.data\.\*\.is\_public | boolean | 
action\_result\.data\.\*\.organization\_id | numeric | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.problem\_id | string | 
action\_result\.data\.\*\.raw\_subject | string | 
action\_result\.data\.\*\.recipient | string | 
action\_result\.data\.\*\.requester\_id | numeric | 
action\_result\.data\.\*\.requester\_id\_name | string | 
action\_result\.data\.\*\.result\_type | string | 
action\_result\.data\.\*\.satisfaction\_probability | string | 
action\_result\.data\.\*\.satisfaction\_rating | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.subject | string | 
action\_result\.data\.\*\.submitter\_id | numeric | 
action\_result\.data\.\*\.submitter\_id\_name | string | 
action\_result\.data\.\*\.tags | string | 
action\_result\.data\.\*\.ticket\_form\_id | numeric | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.updated\_at | string | 
action\_result\.data\.\*\.url | string |  `url`  `domain` 
action\_result\.data\.\*\.via\.channel | string | 
action\_result\.data\.\*\.via\.source\.rel | string | 
action\_result\.summary\.returned\_tickets | numeric | 
action\_result\.summary\.total\_tickets | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.fields\.\*\.id | numeric | 
action\_result\.data\.\*\.fields\.\*\.value | string | 
action\_result\.data\.\*\.custom\_fields\.\*\.id | numeric | 
action\_result\.data\.\*\.custom\_fields\.\*\.value | string |   

## action: 'list tickets'
Get a list of Tickets

Type: **generic**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**max\_results\_per\_page** |  optional  | Max number of tickets to return per page | numeric | 
**page\_number** |  optional  | The page number to get | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.max\_results\_per\_page | numeric | 
action\_result\.parameter\.page\_number | numeric | 
action\_result\.data\.\*\.allow\_attachments | boolean | 
action\_result\.data\.\*\.allow\_channelback | boolean | 
action\_result\.data\.\*\.assignee\_id | numeric | 
action\_result\.data\.\*\.assignee\_id\_name | string | 
action\_result\.data\.\*\.brand\_id | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.due\_at | string | 
action\_result\.data\.\*\.external\_id | string | 
action\_result\.data\.\*\.forum\_topic\_id | string | 
action\_result\.data\.\*\.group\_id | numeric | 
action\_result\.data\.\*\.has\_incidents | boolean | 
action\_result\.data\.\*\.id | numeric |  `zendesk ticket id` 
action\_result\.data\.\*\.is\_public | boolean | 
action\_result\.data\.\*\.organization\_id | numeric | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.problem\_id | string | 
action\_result\.data\.\*\.raw\_subject | string | 
action\_result\.data\.\*\.recipient | string | 
action\_result\.data\.\*\.requester\_id | numeric | 
action\_result\.data\.\*\.requester\_id\_name | string | 
action\_result\.data\.\*\.satisfaction\_probability | string | 
action\_result\.data\.\*\.satisfaction\_rating | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.subject | string | 
action\_result\.data\.\*\.submitter\_id | numeric | 
action\_result\.data\.\*\.submitter\_id\_name | string | 
action\_result\.data\.\*\.tags | string | 
action\_result\.data\.\*\.ticket\_form\_id | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.updated\_at | string | 
action\_result\.data\.\*\.url | string |  `url`  `domain` 
action\_result\.data\.\*\.via\.channel | string | 
action\_result\.data\.\*\.via\.source\.rel | string | 
action\_result\.summary\.total\_tickets | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.fields\.\*\.id | numeric | 
action\_result\.data\.\*\.fields\.\*\.value | string | 
action\_result\.data\.\*\.custom\_fields\.\*\.id | numeric | 
action\_result\.data\.\*\.custom\_fields\.\*\.value | string |   

## action: 'create ticket'
Create a Ticket

Type: **generic**  
Read only: **False**

If you want to assign the value to custom fields, use the following format in "fields" parameter<br>\{"custom\_fields"\: \[\{"Test Field"\: "test field value"\}, \{"custom test field"\: "custom test field value"\}\]\}\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**subject** |  required  | Ticket Subject | string | 
**description** |  required  | Ticket Description | string | 
**fields** |  optional  | Json containing field values | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.description | string | 
action\_result\.parameter\.fields | string | 
action\_result\.parameter\.subject | string | 
action\_result\.data\.\*\.allow\_attachments | boolean | 
action\_result\.data\.\*\.allow\_channelback | boolean | 
action\_result\.data\.\*\.assignee\_id | numeric | 
action\_result\.data\.\*\.assignee\_id\_name | string | 
action\_result\.data\.\*\.brand\_id | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.due\_at | string | 
action\_result\.data\.\*\.external\_id | string | 
action\_result\.data\.\*\.forum\_topic\_id | string | 
action\_result\.data\.\*\.group\_id | numeric | 
action\_result\.data\.\*\.has\_incidents | boolean | 
action\_result\.data\.\*\.id | numeric |  `zendesk ticket id` 
action\_result\.data\.\*\.is\_public | boolean | 
action\_result\.data\.\*\.organization\_id | numeric | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.problem\_id | string | 
action\_result\.data\.\*\.raw\_subject | string | 
action\_result\.data\.\*\.recipient | string | 
action\_result\.data\.\*\.requester\_id | numeric | 
action\_result\.data\.\*\.requester\_id\_name | string | 
action\_result\.data\.\*\.satisfaction\_probability | string | 
action\_result\.data\.\*\.satisfaction\_rating | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.subject | string | 
action\_result\.data\.\*\.submitter\_id | numeric | 
action\_result\.data\.\*\.submitter\_id\_name | string | 
action\_result\.data\.\*\.tags | string | 
action\_result\.data\.\*\.ticket\_form\_id | numeric | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.updated\_at | string | 
action\_result\.data\.\*\.url | string |  `url`  `domain` 
action\_result\.data\.\*\.via\.channel | string | 
action\_result\.data\.\*\.via\.source\.rel | string | 
action\_result\.summary\.created\_ticket\_id | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.fields\.\*\.id | numeric | 
action\_result\.data\.\*\.fields\.\*\.value | string | 
action\_result\.data\.\*\.custom\_fields\.\*\.id | numeric | 
action\_result\.data\.\*\.custom\_fields\.\*\.value | string |   

## action: 'get ticket'
Get ticket information

Type: **generic**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket ID | string |  `zendesk ticket id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.id | string |  `zendesk ticket id` 
action\_result\.data\.\*\.allow\_attachments | boolean | 
action\_result\.data\.\*\.allow\_channelback | boolean | 
action\_result\.data\.\*\.assignee\_id | numeric | 
action\_result\.data\.\*\.assignee\_id\_name | string | 
action\_result\.data\.\*\.brand\_id | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.due\_at | string | 
action\_result\.data\.\*\.external\_id | string | 
action\_result\.data\.\*\.forum\_topic\_id | string | 
action\_result\.data\.\*\.group\_id | numeric | 
action\_result\.data\.\*\.has\_incidents | boolean | 
action\_result\.data\.\*\.id | numeric |  `zendesk ticket id` 
action\_result\.data\.\*\.is\_public | boolean | 
action\_result\.data\.\*\.organization\_id | numeric | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.problem\_id | string | 
action\_result\.data\.\*\.raw\_subject | string | 
action\_result\.data\.\*\.recipient | string | 
action\_result\.data\.\*\.requester\_id | numeric | 
action\_result\.data\.\*\.requester\_id\_name | string | 
action\_result\.data\.\*\.satisfaction\_probability | string | 
action\_result\.data\.\*\.satisfaction\_rating | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.subject | string | 
action\_result\.data\.\*\.submitter\_id | numeric | 
action\_result\.data\.\*\.submitter\_id\_name | string | 
action\_result\.data\.\*\.tags | string | 
action\_result\.data\.\*\.ticket\_form\_id | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.updated\_at | string | 
action\_result\.data\.\*\.url | string |  `url`  `domain` 
action\_result\.data\.\*\.via\.channel | string | 
action\_result\.data\.\*\.via\.source\.rel | string | 
action\_result\.summary\.queried\_ticket\_id | numeric | 
action\_result\.summary\.total\_tickets | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.fields\.\*\.id | numeric | 
action\_result\.data\.\*\.fields\.\*\.value | string | 
action\_result\.data\.\*\.custom\_fields\.\*\.id | numeric | 
action\_result\.data\.\*\.custom\_fields\.\*\.value | string |   

## action: 'update ticket'
Update ticket information

Type: **generic**  
Read only: **False**

Update an already existing ticket with the values that are specified in the 'fields' parameter\. The user has to know the key names to set in this parameter\. Please refer to the Zendesk Core API, Tickets section to learn about the fields that can be used to update or create tickets\.<br>The JSON that is specified in the 'fields' parameter should have the keys and values specified in double quotes string format, except in case of boolean values, which should be either <i>true</i> or <i>false</i>\.<br>Some examples\: <ul><li>To close a ticket\: \{"subject"\: "Zeus, multiple action need to be taken", "status"\: "solved"\}</li><li>To add a comment\: \{"status"\: "open", "comment"\: \{ "body"\: "The smoke is very colorful\.", "author\_id"\: 1 \}\}</li><li>To update custom fields value\: \{"custom\_fields"\: \[\{"Test Field"\: "test field value"\}, \{"custom test field"\: "custom test field value"\}\]\}</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**id** |  required  | Ticket ID | string |  `zendesk ticket id` 
**fields** |  required  | Json containing field values | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.fields | string | 
action\_result\.parameter\.id | string |  `zendesk ticket id` 
action\_result\.data\.\*\.allow\_attachments | boolean | 
action\_result\.data\.\*\.allow\_channelback | boolean | 
action\_result\.data\.\*\.assignee\_id | numeric | 
action\_result\.data\.\*\.assignee\_id\_name | string | 
action\_result\.data\.\*\.brand\_id | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.due\_at | string | 
action\_result\.data\.\*\.external\_id | string | 
action\_result\.data\.\*\.forum\_topic\_id | string | 
action\_result\.data\.\*\.group\_id | numeric | 
action\_result\.data\.\*\.has\_incidents | boolean | 
action\_result\.data\.\*\.id | numeric |  `zendesk ticket id` 
action\_result\.data\.\*\.is\_public | boolean | 
action\_result\.data\.\*\.organization\_id | numeric | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.problem\_id | string | 
action\_result\.data\.\*\.raw\_subject | string | 
action\_result\.data\.\*\.recipient | string | 
action\_result\.data\.\*\.requester\_id | numeric | 
action\_result\.data\.\*\.requester\_id\_name | string | 
action\_result\.data\.\*\.satisfaction\_probability | string | 
action\_result\.data\.\*\.satisfaction\_rating | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.subject | string | 
action\_result\.data\.\*\.submitter\_id | numeric | 
action\_result\.data\.\*\.submitter\_id\_name | string | 
action\_result\.data\.\*\.tags | string | 
action\_result\.data\.\*\.ticket\_form\_id | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.updated\_at | string | 
action\_result\.data\.\*\.url | string |  `url`  `domain` 
action\_result\.data\.\*\.via\.channel | string | 
action\_result\.data\.\*\.via\.source\.rel | string | 
action\_result\.summary\.total\_tickets | numeric | 
action\_result\.summary\.updated\_ticket\_id | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.data\.\*\.fields\.\*\.id | numeric | 
action\_result\.data\.\*\.fields\.\*\.value | string | 
action\_result\.data\.\*\.custom\_fields\.\*\.id | numeric | 
action\_result\.data\.\*\.custom\_fields\.\*\.value | string | 