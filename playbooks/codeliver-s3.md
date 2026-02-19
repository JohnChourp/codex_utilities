# CodeDeliver S3 buckets (df account)

- Generated: 2026-01-25T12:36Z
- AWS profile: df
- Region (default): eu-west-1
- Filters: bucket name starts with `codeliver-`

## codeliver-app

- Bucket ARN: `arn:aws:s3:::codeliver-app`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-app/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-app\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-app-dev

- Bucket ARN: `arn:aws:s3:::codeliver-app-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-app-dev/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-app-dev\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-cost-wizard-react

- Bucket ARN: `arn:aws:s3:::codeliver-cost-wizard-react`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": true
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-cost-wizard-react/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerPreferred"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-groups

- Bucket ARN: `arn:aws:s3:::codeliver-groups`
- Bucket Region: `eu-west-1`

### Versioning

```json
{
  "Status": "Enabled"
}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

Error: An error occurred (NoSuchWebsiteConfiguration) when calling the GetBucketWebsite operation: The specified bucket does not have a website configuration

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-groups/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-groups\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{
  "Status": "Enabled"
}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-io

- Bucket ARN: `arn:aws:s3:::codeliver-io`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

```json
{
  "ErrorDocument": {
    "Key": "index.html"
  },
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": true,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-io/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-io-dev

- Bucket ARN: `arn:aws:s3:::codeliver-io-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

```json
{
  "ErrorDocument": {
    "Key": "index.html"
  },
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": true,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-io-dev/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-json-polylines

- Bucket ARN: `arn:aws:s3:::codeliver-json-polylines`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

Error: An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicy operation: The bucket policy does not exist

### PolicyStatus

Error: An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicyStatus operation: The bucket policy does not exist

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "ObjectWriter"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-node-localserver

- Bucket ARN: `arn:aws:s3:::codeliver-node-localserver`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

Error: An error occurred (NoSuchWebsiteConfiguration) when calling the GetBucketWebsite operation: The specified bucket does not have a website configuration

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2008-10-17\",\"Id\":\"PolicyForCloudFrontPrivateContent\",\"Statement\":[{\"Sid\":\"1\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E31SNXOJDE8VP9\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-node-localserver/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": false
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

```json
{
  "TagSet": [
    {
      "Key": "bucket",
      "Value": "codeliver-localserver"
    },
    {
      "Key": "project",
      "Value": "codeliver"
    }
  ]
}
```

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-panel

- Bucket ARN: `arn:aws:s3:::codeliver-panel`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-panel/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-panel\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-panel-dev

- Bucket ARN: `arn:aws:s3:::codeliver-panel-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-panel-dev/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-panel-dev\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-pos

- Bucket ARN: `arn:aws:s3:::codeliver-pos`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-pos/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-pos\"},{\"Sid\":\"AllowCloudFrontServicePrincipal\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"cloudfront.amazonaws.com\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-pos/*\",\"Condition\":{\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:cloudfront::957873067375:distribution/E33CR68T9T6GY7\"}}}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-pos-dev

- Bucket ARN: `arn:aws:s3:::codeliver-pos-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET",
        "PUT"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":[\"s3:GetObject\",\"s3:PutObject\",\"s3:PutObjectAcl\"],\"Resource\":\"arn:aws:s3:::codeliver-pos-dev/*\"},{\"Sid\":\"AllowListObjects\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:ListBucket\",\"Resource\":\"arn:aws:s3:::codeliver-pos-dev\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

```json
{
  "TagSet": [
    {
      "Key": "bucket",
      "Value": "codeliverpos"
    }
  ]
}
```

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-sap

- Bucket ARN: `arn:aws:s3:::codeliver-sap`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-sap/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "ObjectWriter"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

```json
{
  "TagSet": [
    {
      "Key": "bucket",
      "Value": "codeliversap"
    }
  ]
}
```

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-sap-dev

- Bucket ARN: `arn:aws:s3:::codeliver-sap-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": [
        "*"
      ],
      "AllowedMethods": [
        "GET"
      ],
      "AllowedOrigins": [
        "*"
      ],
      "MaxAgeSeconds": 0
    }
  ]
}
```

### Website

```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  }
}
```

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "BlockPublicPolicy": false,
    "IgnorePublicAcls": false,
    "RestrictPublicBuckets": false
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AddPerm\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-sap-dev/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": true
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "ObjectWriter"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

```json
{
  "TagSet": [
    {
      "Key": "bucket",
      "Value": "codeliversapdev"
    }
  ]
}
```

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-socket-pings

- Bucket ARN: `arn:aws:s3:::codeliver-socket-pings`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": false
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

Error: An error occurred (NoSuchWebsiteConfiguration) when calling the GetBucketWebsite operation: The specified bucket does not have a website configuration

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "BlockPublicPolicy": true,
    "IgnorePublicAcls": true,
    "RestrictPublicBuckets": true
  }
}
```

### Policy

Error: An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicy operation: The bucket policy does not exist

### PolicyStatus

Error: An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicyStatus operation: The bucket policy does not exist

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "ObjectWriter"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

```json
{
  "TagSet": [
    {
      "Key": "bucket",
      "Value": "socket-pings"
    },
    {
      "Key": "project",
      "Value": "codeliver"
    }
  ]
}
```

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-templates-app

- Bucket ARN: `arn:aws:s3:::codeliver-templates-app`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": true
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

Error: An error occurred (NoSuchWebsiteConfiguration) when calling the GetBucketWebsite operation: The specified bucket does not have a website configuration

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "BlockPublicPolicy": true,
    "IgnorePublicAcls": true,
    "RestrictPublicBuckets": true
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2008-10-17\",\"Id\":\"PolicyForCloudFrontPrivateContent\",\"Statement\":[{\"Sid\":\"1\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E2ECB6K1P2TTUO\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-templates-app/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": false
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```

## codeliver-templates-app-dev

- Bucket ARN: `arn:aws:s3:::codeliver-templates-app-dev`
- Bucket Region: `eu-west-1`

### Versioning

```json
{}
```

### Encryption

```json
{
  "ServerSideEncryptionConfiguration": {
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        },
        "BucketKeyEnabled": true
      }
    ]
  }
}
```

### Lifecycle

Error: An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist

### Cors

Error: An error occurred (NoSuchCORSConfiguration) when calling the GetBucketCors operation: The CORS configuration does not exist

### Website

Error: An error occurred (NoSuchWebsiteConfiguration) when calling the GetBucketWebsite operation: The specified bucket does not have a website configuration

### Logging

```json
{}
```

### PublicAccessBlock

```json
{
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": true,
    "BlockPublicPolicy": true,
    "IgnorePublicAcls": true,
    "RestrictPublicBuckets": true
  }
}
```

### Policy

```json
{
  "Policy": "{\"Version\":\"2008-10-17\",\"Id\":\"PolicyForCloudFrontPrivateContent\",\"Statement\":[{\"Sid\":\"1\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity EC3218CUVJTSW\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::codeliver-templates-app-dev/*\"}]}"
}
```

### PolicyStatus

```json
{
  "PolicyStatus": {
    "IsPublic": false
  }
}
```

### Replication

Error: An error occurred (ReplicationConfigurationNotFoundError) when calling the GetBucketReplication operation: The replication configuration was not found

### OwnershipControls

```json
{
  "OwnershipControls": {
    "Rules": [
      {
        "ObjectOwnership": "BucketOwnerEnforced"
      }
    ]
  }
}
```

### Accelerate

```json
{}
```

### RequestPayment

```json
{
  "Payer": "BucketOwner"
}
```

### Tagging

Error: An error occurred (NoSuchTagSet) when calling the GetBucketTagging operation: The TagSet does not exist

### ObjectLock

Error: An error occurred (ObjectLockConfigurationNotFoundError) when calling the GetObjectLockConfiguration operation: Object Lock configuration does not exist for this bucket

### Notification

```json
{}
```
