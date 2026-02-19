# CodeDeliver API Gateways (df account)

- Generated: 2026-01-25T12:04Z
- AWS profile: df
- Region: eu-west-1
- Filters: API name starts with `codeliver-`

## REST APIs

### codeliver-panel (0ws8y1lcy5)

#### RestApi

```json
{
  "apiKeySource": "HEADER",
  "apiStatus": "AVAILABLE",
  "createdDate": "2023-06-14T15:43:52+03:00",
  "disableExecuteApiEndpoint": false,
  "endpointConfiguration": {
    "types": [
      "REGIONAL"
    ]
  },
  "id": "0ws8y1lcy5",
  "name": "codeliver-panel",
  "rootResourceId": "7cjwbitvni",
  "securityPolicy": "TLS_1_0",
  "tags": {}
}
```

#### Stages

```json
{
  "item": [
    {
      "cacheClusterEnabled": false,
      "cacheClusterSize": "0.5",
      "cacheClusterStatus": "NOT_AVAILABLE",
      "createdDate": "2023-06-14T16:05:33+03:00",
      "deploymentId": "52hxfh",
      "lastUpdatedDate": "2026-01-14T08:14:56+02:00",
      "methodSettings": {
        "*/*": {
          "cacheDataEncrypted": false,
          "cacheTtlInSeconds": 300,
          "cachingEnabled": false,
          "dataTraceEnabled": false,
          "loggingLevel": "OFF",
          "metricsEnabled": false,
          "requireAuthorizationForCacheControl": true,
          "throttlingBurstLimit": 5000,
          "throttlingRateLimit": 10000.0,
          "unauthorizedCacheControlHeaderStrategy": "SUCCEED_WITH_RESPONSE_HEADER"
        }
      },
      "stageName": "prod",
      "tracingEnabled": false
    }
  ]
}
```

#### Tags

```json
{
  "tags": {}
}
```

## Manual updates (2026-02-18)

- Added SAP route-control endpoints used by Control Panel fullscreen modal:
  - `POST /prod/codeliver-sap-fetch-routes`
  - `POST /prod/codeliver-sap-fetch-routes-paths`
  - `POST /prod/codeliver-sap-handle-route`
- Extended existing endpoint:
  - `POST /prod/codeliver-sap-fetch-delivery-requests` with `type: "fetch-requests-by-route-id"` (requires `group` + `route_id` in body).

### codeliver-app (8sw8osiclf)

#### RestApi

```json
{
  "apiKeySource": "HEADER",
  "apiStatus": "AVAILABLE",
  "createdDate": "2023-06-14T18:24:39+03:00",
  "disableExecuteApiEndpoint": false,
  "endpointConfiguration": {
    "types": [
      "REGIONAL"
    ]
  },
  "id": "8sw8osiclf",
  "name": "codeliver-app",
  "rootResourceId": "s39yj9ctgb",
  "securityPolicy": "TLS_1_0",
  "tags": {}
}
```

#### Stages

```json
{
  "item": [
    {
      "cacheClusterEnabled": false,
      "cacheClusterStatus": "NOT_AVAILABLE",
      "createdDate": "2023-07-27T11:24:16+03:00",
      "deploymentId": "8wgwp4",
      "lastUpdatedDate": "2026-01-19T10:52:28+02:00",
      "methodSettings": {},
      "stageName": "prod",
      "tracingEnabled": false
    }
  ]
}
```

#### Tags

```json
{
  "tags": {}
}
```

### codeliver-pos (n4motxwuya)

#### RestApi

```json
{
  "apiKeySource": "HEADER",
  "apiStatus": "AVAILABLE",
  "createdDate": "2023-06-14T18:25:20+03:00",
  "disableExecuteApiEndpoint": false,
  "endpointConfiguration": {
    "types": [
      "REGIONAL"
    ]
  },
  "id": "n4motxwuya",
  "name": "codeliver-pos",
  "rootResourceId": "k9oy2me466",
  "securityPolicy": "TLS_1_0",
  "tags": {}
}
```

#### Stages

```json
{
  "item": [
    {
      "cacheClusterEnabled": false,
      "cacheClusterStatus": "NOT_AVAILABLE",
      "createdDate": "2023-06-26T10:51:07+03:00",
      "deploymentId": "2qnttd",
      "lastUpdatedDate": "2026-01-14T08:08:22+02:00",
      "methodSettings": {},
      "stageName": "prod",
      "tracingEnabled": false
    }
  ]
}
```

#### Tags

```json
{
  "tags": {}
}
```

### codeliver-sap (y3hl4t4f22)

#### RestApi

```json
{
  "apiKeySource": "HEADER",
  "apiStatus": "AVAILABLE",
  "createdDate": "2023-06-22T14:29:22+03:00",
  "disableExecuteApiEndpoint": false,
  "endpointConfiguration": {
    "types": [
      "REGIONAL"
    ]
  },
  "id": "y3hl4t4f22",
  "name": "codeliver-sap",
  "rootResourceId": "4gvf8ym0b5",
  "securityPolicy": "TLS_1_0",
  "tags": {}
}
```

#### Stages

```json
{
  "item": [
    {
      "cacheClusterEnabled": false,
      "cacheClusterStatus": "NOT_AVAILABLE",
      "createdDate": "2023-06-22T15:05:35+03:00",
      "deploymentId": "7e36v3",
      "lastUpdatedDate": "2026-01-13T16:14:25+02:00",
      "methodSettings": {},
      "stageName": "prod",
      "tracingEnabled": false
    }
  ]
}
```

#### Tags

```json
{
  "tags": {}
}
```

## HTTP/WebSocket APIs

### codeliver-panel-ws (5ihos3os2j)

#### Api

```json
{
  "ApiEndpoint": "wss://5ihos3os2j.execute-api.eu-west-1.amazonaws.com",
  "ApiId": "5ihos3os2j",
  "ApiKeySelectionExpression": "$request.header.x-api-key",
  "CreatedDate": "2023-06-19T10:45:12+00:00",
  "DisableExecuteApiEndpoint": false,
  "Name": "codeliver-panel-ws",
  "ProtocolType": "WEBSOCKET",
  "RouteSelectionExpression": "$request.body.type",
  "Tags": {}
}
```

#### Stages

```json
{
  "Items": [
    {
      "CreatedDate": "2023-06-19T10:45:16+00:00",
      "DefaultRouteSettings": {
        "DataTraceEnabled": false,
        "DetailedMetricsEnabled": false,
        "LoggingLevel": "OFF"
      },
      "DeploymentId": "fukmnx",
      "LastUpdatedDate": "2023-06-29T07:58:49+00:00",
      "RouteSettings": {},
      "StageName": "production",
      "StageVariables": {},
      "Tags": {}
    }
  ]
}
```

#### Routes

```json
{
  "Items": [
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "c0ixwb8",
      "RouteKey": "cloud-command-response",
      "Target": "integrations/crr3xf2"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "c7x8ier",
      "RouteKey": "$default",
      "Target": "integrations/shsirjf"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "iy1cuil",
      "RouteKey": "user-test-connection",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/p3adfxh"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "m1ww9n8",
      "RouteKey": "$disconnect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/xka4bb5"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "CUSTOM",
      "AuthorizerId": "dptta3",
      "RouteId": "zq20lzt",
      "RouteKey": "$connect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/jll3j13"
    }
  ]
}
```

#### Integrations

```json
{
  "Items": [
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "crr3xf2",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-panel-ws-cloud-command-response/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "jll3j13",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-panel-ws-connect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "ContentHandlingStrategy": "CONVERT_TO_TEXT",
      "IntegrationId": "p3adfxh",
      "IntegrationMethod": "POST",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "RequestTemplates": {
        "200": "{\"statusCode\": 200}"
      },
      "TemplateSelectionExpression": "200",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "shsirjf",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "xka4bb5",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-panel-ws-disconnect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    }
  ]
}
```

#### Authorizers

```json
{
  "Items": [
    {
      "AuthorizerId": "dptta3",
      "AuthorizerType": "REQUEST",
      "AuthorizerUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-panel-authorizer/invocations",
      "IdentitySource": [
        "route.request.querystring.Authorization"
      ],
      "Name": "codeliver-panel-authorizer"
    }
  ]
}
```

### codeliver-sap-ws (ao1eg66vyg)

#### Api

```json
{
  "ApiEndpoint": "wss://ao1eg66vyg.execute-api.eu-west-1.amazonaws.com",
  "ApiId": "ao1eg66vyg",
  "ApiKeySelectionExpression": "$request.header.x-api-key",
  "CreatedDate": "2023-06-27T07:31:02+00:00",
  "DisableExecuteApiEndpoint": false,
  "Name": "codeliver-sap-ws",
  "ProtocolType": "WEBSOCKET",
  "RouteSelectionExpression": "$request.body.type",
  "Tags": {}
}
```

#### Stages

```json
{
  "Items": [
    {
      "CreatedDate": "2023-06-27T07:31:05+00:00",
      "DefaultRouteSettings": {
        "DataTraceEnabled": false,
        "DetailedMetricsEnabled": false,
        "LoggingLevel": "OFF"
      },
      "DeploymentId": "c1m3we",
      "LastUpdatedDate": "2023-06-29T07:58:31+00:00",
      "RouteSettings": {},
      "StageName": "production",
      "StageVariables": {},
      "Tags": {}
    }
  ]
}
```

#### Routes

```json
{
  "Items": [
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "1yi63jo",
      "RouteKey": "user-test-connection",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/3ccxgo4"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "akmrfx9",
      "RouteKey": "$disconnect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/oae5pz2"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "CUSTOM",
      "AuthorizerId": "06ad9f",
      "RouteId": "hu48czc",
      "RouteKey": "$connect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/6qvc51h"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "q8i9l25",
      "RouteKey": "codeliver-sap-ws-cloud-command-response",
      "Target": "integrations/fxd6n23"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "wko8rlq",
      "RouteKey": "$default",
      "Target": "integrations/m262z2n"
    }
  ]
}
```

#### Integrations

```json
{
  "Items": [
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "3ccxgo4",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "RequestTemplates": {
        "200": "{\"statusCode\": 200}"
      },
      "TemplateSelectionExpression": "200",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "6qvc51h",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-sap-ws-connect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "fxd6n23",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-sap-ws-cloud-command-response/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "m262z2n",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "oae5pz2",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-sap-ws-disconnect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    }
  ]
}
```

#### Authorizers

```json
{
  "Items": [
    {
      "AuthorizerId": "06ad9f",
      "AuthorizerType": "REQUEST",
      "AuthorizerUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-sap-authorizer/invocations",
      "IdentitySource": [
        "route.request.querystring.Authorizer"
      ],
      "Name": "codeliver-sap-authorizer"
    }
  ]
}
```

### codeliver-pos-ws (fkv3qt0ci0)

#### Api

```json
{
  "ApiEndpoint": "wss://fkv3qt0ci0.execute-api.eu-west-1.amazonaws.com",
  "ApiId": "fkv3qt0ci0",
  "ApiKeySelectionExpression": "$request.header.x-api-key",
  "CreatedDate": "2023-06-27T08:44:54+00:00",
  "DisableExecuteApiEndpoint": false,
  "Name": "codeliver-pos-ws",
  "ProtocolType": "WEBSOCKET",
  "RouteSelectionExpression": "$request.body.type",
  "Tags": {}
}
```

#### Stages

```json
{
  "Items": [
    {
      "CreatedDate": "2023-06-27T08:44:57+00:00",
      "DefaultRouteSettings": {
        "DataTraceEnabled": false,
        "DetailedMetricsEnabled": false,
        "LoggingLevel": "OFF"
      },
      "DeploymentId": "jbhtqy",
      "LastUpdatedDate": "2025-10-24T09:39:00+00:00",
      "RouteSettings": {},
      "StageName": "production",
      "StageVariables": {},
      "Tags": {}
    }
  ]
}
```

#### Routes

```json
{
  "Items": [
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "7on9q9a",
      "RouteKey": "codeliver-pos-ws-cloud-command-response",
      "Target": "integrations/pt36ez2"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "CUSTOM",
      "AuthorizerId": "gig4js",
      "RouteId": "9dtl9db",
      "RouteKey": "$connect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/mmuqqun"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "a0xys6k",
      "RouteKey": "user-test-connection",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/uzl9n3f"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "qzcruzb",
      "RouteKey": "$disconnect",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/ut4xwff"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "thnmkxl",
      "RouteKey": "$default",
      "Target": "integrations/qrnnlr8"
    }
  ]
}
```

#### Integrations

```json
{
  "Items": [
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "mmuqqun",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-pos-ws-connect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "pt36ez2",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-pos-ws-cloud-command-response/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "qrnnlr8",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "ut4xwff",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-pos-ws-disconnect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "uzl9n3f",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "RequestTemplates": {
        "200": "{\"statusCode\": 200}"
      },
      "TemplateSelectionExpression": "200",
      "TimeoutInMillis": 29000
    }
  ]
}
```

#### Authorizers

```json
{
  "Items": [
    {
      "AuthorizerId": "gig4js",
      "AuthorizerType": "REQUEST",
      "AuthorizerUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-pos-authorizer/invocations",
      "IdentitySource": [
        "route.request.querystring.Authorization"
      ],
      "Name": "codeliver-pos-authorizer"
    }
  ]
}
```

### codeliver-localserver (os1phxl7xb)

#### Api

```json
{
  "ApiEndpoint": "wss://os1phxl7xb.execute-api.eu-west-1.amazonaws.com",
  "ApiId": "os1phxl7xb",
  "ApiKeySelectionExpression": "$request.header.x-api-key",
  "CreatedDate": "2023-06-29T16:05:25+00:00",
  "DisableExecuteApiEndpoint": false,
  "Name": "codeliver-localserver",
  "ProtocolType": "WEBSOCKET",
  "RouteSelectionExpression": "$request.body.type",
  "Tags": {}
}
```

#### Stages

```json
{
  "Items": [
    {
      "CreatedDate": "2023-06-29T16:05:29+00:00",
      "DefaultRouteSettings": {
        "DataTraceEnabled": false,
        "DetailedMetricsEnabled": false,
        "LoggingLevel": "OFF"
      },
      "DeploymentId": "qa9nq0",
      "LastUpdatedDate": "2023-06-29T16:14:28+00:00",
      "RouteSettings": {},
      "StageName": "prod",
      "StageVariables": {},
      "Tags": {}
    }
  ]
}
```

#### Routes

```json
{
  "Items": [
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "05qb8os",
      "RouteKey": "$default"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "0athjui",
      "RouteKey": "cloud-command-response",
      "Target": "integrations/vdicx05"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "klfumo1",
      "RouteKey": "localserver-ping",
      "Target": "integrations/jtwbv30"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "n8d2orr",
      "RouteKey": "$connect",
      "Target": "integrations/ggj63eu"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "q3okh9g",
      "RouteKey": "localserver-log",
      "Target": "integrations/pbd1rdb"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "r2w3rzm",
      "RouteKey": "localserver-test-connection",
      "RouteResponseSelectionExpression": "$default",
      "Target": "integrations/e963l9n"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "wtcn7ar",
      "RouteKey": "$disconnect",
      "Target": "integrations/tdmfwbp"
    },
    {
      "ApiKeyRequired": false,
      "AuthorizationType": "NONE",
      "RouteId": "z6qgpxo",
      "RouteKey": "connect-group-store",
      "Target": "integrations/hl73axh"
    }
  ]
}
```

#### Integrations

```json
{
  "Items": [
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "e963l9n",
      "IntegrationResponseSelectionExpression": "${integration.response.statuscode}",
      "IntegrationType": "MOCK",
      "PassthroughBehavior": "WHEN_NO_TEMPLATES",
      "PayloadFormatVersion": "1.0",
      "RequestTemplates": {
        "200": "{\"statusCode\": 200}"
      },
      "TemplateSelectionExpression": "200",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "ggj63eu",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-connect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "ContentHandlingStrategy": "CONVERT_TO_TEXT",
      "IntegrationId": "hl73axh",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-connect-group-store/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "ContentHandlingStrategy": "CONVERT_TO_TEXT",
      "IntegrationId": "jtwbv30",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-ping/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "ContentHandlingStrategy": "CONVERT_TO_TEXT",
      "IntegrationId": "pbd1rdb",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-log/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "IntegrationId": "tdmfwbp",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-disconnect/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    },
    {
      "ConnectionType": "INTERNET",
      "ContentHandlingStrategy": "CONVERT_TO_TEXT",
      "IntegrationId": "vdicx05",
      "IntegrationMethod": "POST",
      "IntegrationType": "AWS_PROXY",
      "IntegrationUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:957873067375:function:codeliver-localserver-ws-cloud-command-response/invocations",
      "PassthroughBehavior": "WHEN_NO_MATCH",
      "PayloadFormatVersion": "1.0",
      "TimeoutInMillis": 29000
    }
  ]
}
```

#### Authorizers

```json
{
  "Items": []
}
```
