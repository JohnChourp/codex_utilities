# CodeDeliver DynamoDB kinesis triggers

> Canonical DynamoDB table -> Kinesis data stream mapping for CodeDeliver.
>
> **Single source of truth:** this file must exist only once under:
>
> - `.codex/playbooks/codeliver-dynamodb-kinesis-triggers.md`
>
> Rules:
>
> - Do **NOT** copy this file into any repo/lambda/project folder.
> - Do **NOT** create additional `playbooks/` directories elsewhere.
> - If Kinesis mappings are missing, verify from IaC/code and update **this** canonical file.

## Scope

Canonical mapping of DynamoDB tables with known Kinesis data stream connections.

Only include verified connections. If a table is not listed, verify from IaC/code before adding.

## Notation conventions

- If anything is unknown, keep it explicit:
  - `TBD: verify from IaC` (do not guess)

## Tables

### codeliver-devices-sockets

Amazon Kinesis data stream details

- codeliver-sockets: Data retention period = 1 day, Maximum record size = 1024 KiB, Capacity mode = Provisioned, Write capacity Maximum = 1 MiB/second 1,000 records/second, Read capacity Maximum = 2 MiB/second

### codeliver-localserver-sockets

Amazon Kinesis data stream details

- codeliver-sockets: Data retention period = 1 day, Maximum record size = 1024 KiB, Capacity mode = Provisioned, Write capacity Maximum = 1 MiB/second 1,000 records/second, Read capacity Maximum = 2 MiB/second

### codeliver-panel-sockets

Amazon Kinesis data stream details

- codeliver-sockets: Data retention period = 1 day, Maximum record size = 1024 KiB, Capacity mode = Provisioned, Write capacity Maximum = 1 MiB/second 1,000 records/second, Read capacity Maximum = 2 MiB/second

### codeliver-pos-sockets

Amazon Kinesis data stream details

- codeliver-sockets: Data retention period = 1 day, Maximum record size = 1024 KiB, Capacity mode = Provisioned, Write capacity Maximum = 1 MiB/second 1,000 records/second, Read capacity Maximum = 2 MiB/second

### codeliver-sap-sockets

Amazon Kinesis data stream details

- codeliver-sockets: Data retention period = 1 day, Maximum record size = 1024 KiB, Capacity mode = Provisioned, Write capacity Maximum = 1 MiB/second 1,000 records/second, Read capacity Maximum = 2 MiB/second
