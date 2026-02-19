# CodeDeliver EventBridge (df account)

- Generated: 2026-01-25T12:31Z
- AWS profile: df
- Region: eu-west-1
- Filters: event bus name starts with `codeliver-`
- Filters (rules): rule name starts with `codeliver-`

## Event buses

No event buses found with prefix `codeliver-`.

## Default event bus rules

- Event bus: `default`

### codeliver-auto-create-route

#### Rule

```json
{
  "Arn": "arn:aws:events:eu-west-1:957873067375:rule/codeliver-auto-create-route",
  "CreatedBy": "957873067375",
  "Description": "Automatically Create Routes",
  "EventBusName": "default",
  "Name": "codeliver-auto-create-route",
  "ScheduleExpression": "rate(1 minute)",
  "State": "ENABLED"
}
```

#### Targets

```json
{
  "Targets": [
    {
      "Arn": "arn:aws:lambda:eu-west-1:957873067375:function:codeliver-auto-create-route",
      "Id": "dlu1nrn1f8mf01m4ee5m",
      "Input": "{\n  \"type\": \"auto-create-route\"\n}"
    }
  ]
}
```

### codeliver-group-data-simulation

#### Rule

```json
{
  "Arn": "arn:aws:events:eu-west-1:957873067375:rule/codeliver-group-data-simulation",
  "CreatedBy": "957873067375",
  "Description": "sending delivery guys coords in simualtion as like they are real",
  "EventBusName": "default",
  "Name": "codeliver-group-data-simulation",
  "ScheduleExpression": "rate(1 minute)",
  "State": "DISABLED"
}
```

#### Targets

```json
{
  "Targets": [
    {
      "Arn": "arn:aws:lambda:eu-west-1:957873067375:function:codeliver-group-data-simulation",
      "Id": "zfbplaj0wwxwr0giu0xp"
    }
  ]
}
```

### codeliver-group-requests-simulation

#### Rule

```json
{
  "Arn": "arn:aws:events:eu-west-1:957873067375:rule/codeliver-group-requests-simulation",
  "CreatedBy": "957873067375",
  "Description": "creates random requests",
  "EventBusName": "default",
  "Name": "codeliver-group-requests-simulation",
  "ScheduleExpression": "rate(1 minute)",
  "State": "DISABLED"
}
```

#### Targets

```json
{
  "Targets": [
    {
      "Arn": "arn:aws:lambda:eu-west-1:957873067375:function:codeliver-group-requests-simulation",
      "Id": "n1rj63aaivcn43fg297x"
    }
  ]
}
```

### codeliver-init-short-order-id

#### Rule

```json
{
  "Arn": "arn:aws:events:eu-west-1:957873067375:rule/codeliver-init-short-order-id",
  "CreatedBy": "957873067375",
  "Description": "reset short order id for stores",
  "EventBusName": "default",
  "Name": "codeliver-init-short-order-id",
  "ScheduleExpression": "cron(0 3 * * ? *)",
  "State": "ENABLED"
}
```

#### Targets

```json
{
  "Targets": [
    {
      "Arn": "arn:aws:lambda:eu-west-1:957873067375:function:codeliver-init-short-order-id",
      "Id": "Id2742cf49-04c3-439d-9206-ae14d7429d18"
    }
  ]
}
```

### codeliver-recalculate-route-and-paths-distances-and-polylines

#### Rule

```json
{
  "Arn": "arn:aws:events:eu-west-1:957873067375:rule/codeliver-recalculate-route-and-paths-distances-and-polylines",
  "CreatedBy": "957873067375",
  "Description": "recalculates route-and-paths-distances-and-polylines for routes that have status accepted ",
  "EventBusName": "default",
  "Name": "codeliver-recalculate-route-and-paths-distances-and-polylines",
  "ScheduleExpression": "rate(2 minutes)",
  "State": "DISABLED"
}
```

#### Targets

```json
{
  "Targets": [
    {
      "Arn": "arn:aws:lambda:eu-west-1:957873067375:function:codeliver-recalculate-route-and-paths-distances-and-polylines",
      "Id": "rm7xpl1sqfrfbno8ia1g",
      "Input": "{\n  \"type\": \"recalculate-route-and-paths-distances-and-polylines-periodically\"\n}"
    }
  ]
}
```
