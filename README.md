# apiTester (v1.1)

## License 
GNU General Public License v3.0

## Prerequisites:
- python 3
- modules:
  - Requests
  - junit-xml

This python tool is based on the requests python module. This script added validation layer to the standard request/response functionality.  

## What is it possible to do with this tool:
 - Method: GET, POST, PUT, DELETE
 - Rest API testing 
 - SOAP API testing
 - GraphQL API testing
 - Json validation
 - Response time validation

## How to use it:

### 1. Create a test file
Create a test file with the following structure:

```json
  {
    "url": "https://petstore.swagger.io",
    "endPoints": [
      {
      "request": {
        "method": "GET",
        "endPoint": "/v2/pet/findByStatus",
        "requestDataParams": {"status":  "pending"},
        "headers" : {}
      },
      "response": {
        "responseStatus": 200,
        "nameTestSuite": "/v2/pet/findByStatusPending",
        "timeoutForActionSec": 10,
        "validationRules": "ResponseStatus~ResponseTimeSec=1~PreviousDataValidation~ParsableJson~GenReport"
      }
    },
    {
      "request": {
        "method": "GET",
        "endPoint": "/v2/pet/findByStatus",
        "requestDataParams": {"status":  "available"},
        "headers" : { }
      },
      "response": {
        "responseStatus": 200,
        "nameTestSuite": "/v2/pet/findByStatusAvailable",
        "timeoutForActionSec": 10,
        "validationRules": "ResponseStatus~ResponseTimeSec=1~ParsableJson~GenReport"
      }
    },
    {
      "request": {
        "method": "GET",
        "endPoint": "/v2/pet/findByStatus",
        "requestDataParams": {"status":  "sold"},
        "headers" : { }
      },
      "response": {
        "responseStatus": 200,
        "nameTestSuite": "/v2/pet/findByStatusSold",
        "timeoutForActionSec": 10,
        "validationRules": "ResponseStatus~ResponseTimeSec=0.3~PreviousDataValidation~ParsableJson~GenReport"
      }
    }
  ]
}
```

### 2. Run the script

```
python apiTester.py --ConfFile=demo/config.json -AuthParams "{\"user\":\"test\", \"Password\": \"test\"}"
```

OR
```
python apiTester.py --ConfFile=demo/config.json
```

[More information on this page](https://www.chlopcik.cz/apitester/)
