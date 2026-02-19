# CodeDeliver SQS queues (df account)

- Generated: 2026-01-25T12:10Z
- AWS profile: df
- Region: eu-west-1

## codeliver-app-socket-emitter-sqs.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-app-socket-emitter-sqs.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-app-socket-emitter-sqs.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1749106081`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1749106081`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-app-socket-emitter-sqs.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-app-socket-emitter-sqs.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-app-users-pings

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-app-users-pings`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-app-users-pings`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1690546771`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1690546771`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-app-users-pings",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2008-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-app-users-pings`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-delivery-guys-coordinates-sqs.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-delivery-guys-coordinates-sqs.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-delivery-guys-coordinates-sqs.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1750058088`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1750058088`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-delivery-guys-coordinates-sqs.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-delivery-guys-coordinates-sqs.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-localserver-socket-emitter-sqs-dlq.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-localserver-socket-emitter-sqs-dlq.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs-dlq.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `false`
- `CreatedTimestamp`: `1688047950`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1688048560`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs-dlq.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs-dlq.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-localserver-socket-emitter-sqs.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-localserver-socket-emitter-sqs.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1688047875`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1690454483`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:codeliver-localserver-socket-emitter-sqs-dlq.fifo",
  "maxReceiveCount": 50
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-localservers-pings

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-localservers-pings`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localservers-pings`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1687940522`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1687940522`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-localservers-pings",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-localservers-pings`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `10`

### Tags

- None

## codeliver-panel-socket-emitter-dlq.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-panel-socket-emitter-dlq.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter-dlq.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687167994`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1687168173`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter-dlq.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter-dlq.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-panel-socket-emitter.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-panel-socket-emitter.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687168328`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1763371827`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:codeliver-panel-socket-emitter-dlq.fifo",
  "maxReceiveCount": 10
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-pings

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-pings`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pings`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1689337987`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1689337987`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `86400`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pings",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pings`
- `ReceiveMessageWaitTimeSeconds`: `5`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pings-dlq",
  "maxReceiveCount": 40
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `8`

### Tags

- None

## codeliver-pings-dlq

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-pings-dlq`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pings-dlq`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1689337784`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1689337784`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pings-dlq",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pings-dlq`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-pos-socket-emitter-dlq.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-pos-socket-emitter-dlq.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter-dlq.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687849615`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1687849615`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter-dlq.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter-dlq.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-pos-socket-emitter.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-pos-socket-emitter.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687849718`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1687849755`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:codeliver-pos-socket-emitter-dlq.fifo",
  "maxReceiveCount": 10
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-retry-sms

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-retry-sms`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1689608509`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1689608509`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:retry-sms-dlq",
  "maxReceiveCount": 10
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `45`

### Tags

- None

## codeliver-retry-sms-dlq

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-retry-sms-dlq`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms-dlq`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1689608417`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1689608417`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms-dlq",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-retry-sms-dlq`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-routes-stream-update-routes-sqs.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-routes-stream-update-routes-sqs.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-routes-stream-update-routes-sqs.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1763378046`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `15`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1769237318`
- `MaximumMessageSize`: `1048576`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-app-socket-emitter-sqs.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-routes-stream-update-routes-sqs.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-sap-socket-emitter-dlq.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-sap-socket-emitter-dlq.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter-dlq.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687850289`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1687850289`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter-dlq.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter-dlq.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-sap-socket-emitter.fifo

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-sap-socket-emitter.fifo`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter.fifo`
- FIFO: `true`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `ContentBasedDeduplication`: `true`
- `CreatedTimestamp`: `1687850368`
- `DeduplicationScope`: `queue`
- `DelaySeconds`: `0`
- `FifoQueue`: `true`
- `FifoThroughputLimit`: `perQueue`
- `LastModifiedTimestamp`: `1687850368`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::957873067375:root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter.fifo",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter.fifo`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `RedrivePolicy`:
```json
{
  "deadLetterTargetArn": "arn:aws:sqs:eu-west-1:957873067375:codeliver-sap-socket-emitter-dlq.fifo",
  "maxReceiveCount": 10
}
```
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None

## codeliver-users-pings

- Queue URL: `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-users-pings`
- Queue ARN: `arn:aws:sqs:eu-west-1:957873067375:codeliver-users-pings`
- FIFO: `false`

### Attributes

- `ApproximateNumberOfMessages`: `0`
- `ApproximateNumberOfMessagesDelayed`: `0`
- `ApproximateNumberOfMessagesNotVisible`: `0`
- `CreatedTimestamp`: `1689683317`
- `DelaySeconds`: `0`
- `LastModifiedTimestamp`: `1689683317`
- `MaximumMessageSize`: `262144`
- `MessageRetentionPeriod`: `345600`
- `Policy`:
```json
{
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Action": "SQS:*",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:sts::957873067375:federated-user/root"
      },
      "Resource": "arn:aws:sqs:eu-west-1:957873067375:codeliver-users-pings",
      "Sid": "__owner_statement"
    }
  ],
  "Version": "2012-10-17"
}
```
- `QueueArn`: `arn:aws:sqs:eu-west-1:957873067375:codeliver-users-pings`
- `ReceiveMessageWaitTimeSeconds`: `0`
- `SqsManagedSseEnabled`: `false`
- `VisibilityTimeout`: `30`

### Tags

- None
