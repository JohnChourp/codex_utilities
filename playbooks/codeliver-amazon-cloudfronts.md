# CodeDeliver CloudFront distributions (df account)

- Generated: 2026-01-25T12:36Z
- AWS profile: df
- Scope: global
- Filters: distribution comment starts with `codeliver-` OR any alias starts with `codeliver-`

## E2SG3UFLQ4AO5E

- DomainName: `d3mal9miugjrrg.cloudfront.net`
- Status: `Deployed`
- Enabled: `true`
- Comment: `codeliver-io dev distribution (created by script)`
- Aliases: `newdev.codeliver.io`
- Match reasons: `comment`

### DistributionConfig

```json
{
  "DistributionConfig": {
    "Aliases": {
      "Items": [
        "newdev.codeliver.io"
      ],
      "Quantity": 1
    },
    "CacheBehaviors": {
      "Quantity": 0
    },
    "CallerReference": "codeliver-io-dev-codeliver-io-dev-1763986078",
    "Comment": "codeliver-io dev distribution (created by script)",
    "ContinuousDeploymentPolicyId": "",
    "CustomErrorResponses": {
      "Quantity": 0
    },
    "DefaultCacheBehavior": {
      "AllowedMethods": {
        "CachedMethods": {
          "Items": [
            "HEAD",
            "GET"
          ],
          "Quantity": 2
        },
        "Items": [
          "HEAD",
          "GET"
        ],
        "Quantity": 2
      },
      "Compress": true,
      "DefaultTTL": 0,
      "FieldLevelEncryptionId": "",
      "ForwardedValues": {
        "Cookies": {
          "Forward": "none"
        },
        "Headers": {
          "Quantity": 0
        },
        "QueryString": false,
        "QueryStringCacheKeys": {
          "Quantity": 0
        }
      },
      "FunctionAssociations": {
        "Quantity": 0
      },
      "GrpcConfig": {
        "Enabled": false
      },
      "LambdaFunctionAssociations": {
        "Quantity": 0
      },
      "MaxTTL": 31536000,
      "MinTTL": 0,
      "SmoothStreaming": false,
      "TargetOriginId": "s3-website-codeliver-io-dev",
      "TrustedKeyGroups": {
        "Enabled": false,
        "Quantity": 0
      },
      "TrustedSigners": {
        "Enabled": false,
        "Quantity": 0
      },
      "ViewerProtocolPolicy": "redirect-to-https"
    },
    "DefaultRootObject": "index.html",
    "Enabled": true,
    "HttpVersion": "http2and3",
    "IsIPV6Enabled": true,
    "Logging": {
      "Bucket": "",
      "Enabled": false,
      "IncludeCookies": false,
      "Prefix": ""
    },
    "OriginGroups": {
      "Quantity": 0
    },
    "Origins": {
      "Items": [
        {
          "ConnectionAttempts": 3,
          "ConnectionTimeout": 10,
          "CustomHeaders": {
            "Quantity": 0
          },
          "CustomOriginConfig": {
            "HTTPPort": 80,
            "HTTPSPort": 443,
            "OriginKeepaliveTimeout": 5,
            "OriginProtocolPolicy": "http-only",
            "OriginReadTimeout": 30,
            "OriginSslProtocols": {
              "Items": [
                "TLSv1",
                "TLSv1.1",
                "TLSv1.2"
              ],
              "Quantity": 3
            }
          },
          "DomainName": "codeliver-io-dev.s3-website-eu-west-1.amazonaws.com",
          "Id": "s3-website-codeliver-io-dev",
          "OriginAccessControlId": "",
          "OriginPath": "",
          "OriginShield": {
            "Enabled": false
          }
        }
      ],
      "Quantity": 1
    },
    "PriceClass": "PriceClass_All",
    "Restrictions": {
      "GeoRestriction": {
        "Quantity": 0,
        "RestrictionType": "none"
      }
    },
    "Staging": false,
    "ViewerCertificate": {
      "ACMCertificateArn": "arn:aws:acm:us-east-1:957873067375:certificate/ee61922e-baa0-4653-b6d1-6ffb9000f448",
      "Certificate": "arn:aws:acm:us-east-1:957873067375:certificate/ee61922e-baa0-4653-b6d1-6ffb9000f448",
      "CertificateSource": "acm",
      "CloudFrontDefaultCertificate": false,
      "MinimumProtocolVersion": "TLSv1.2_2021",
      "SSLSupportMethod": "sni-only"
    },
    "WebACLId": ""
  },
  "ETag": "E317S809YG9V2H"
}
```

### Tags

```json
{
  "Tags": {
    "Items": []
  }
}
```

## E5OBR81Y4BFLT

- DomainName: `d2fykgwgafgjgm.cloudfront.net`
- Status: `Deployed`
- Enabled: `true`
- Comment: `codeliver-io prod distribution (created by script)`
- Aliases: `www.codeliver.io`
- Match reasons: `comment`

### DistributionConfig

```json
{
  "DistributionConfig": {
    "Aliases": {
      "Items": [
        "www.codeliver.io"
      ],
      "Quantity": 1
    },
    "CacheBehaviors": {
      "Quantity": 0
    },
    "CallerReference": "codeliver-io-prod-codeliver-io-1763986062",
    "Comment": "codeliver-io prod distribution (created by script)",
    "ContinuousDeploymentPolicyId": "",
    "CustomErrorResponses": {
      "Quantity": 0
    },
    "DefaultCacheBehavior": {
      "AllowedMethods": {
        "CachedMethods": {
          "Items": [
            "HEAD",
            "GET"
          ],
          "Quantity": 2
        },
        "Items": [
          "HEAD",
          "GET"
        ],
        "Quantity": 2
      },
      "Compress": true,
      "DefaultTTL": 0,
      "FieldLevelEncryptionId": "",
      "ForwardedValues": {
        "Cookies": {
          "Forward": "none"
        },
        "Headers": {
          "Quantity": 0
        },
        "QueryString": false,
        "QueryStringCacheKeys": {
          "Quantity": 0
        }
      },
      "FunctionAssociations": {
        "Quantity": 0
      },
      "GrpcConfig": {
        "Enabled": false
      },
      "LambdaFunctionAssociations": {
        "Quantity": 0
      },
      "MaxTTL": 31536000,
      "MinTTL": 0,
      "SmoothStreaming": false,
      "TargetOriginId": "s3-website-codeliver-io",
      "TrustedKeyGroups": {
        "Enabled": false,
        "Quantity": 0
      },
      "TrustedSigners": {
        "Enabled": false,
        "Quantity": 0
      },
      "ViewerProtocolPolicy": "redirect-to-https"
    },
    "DefaultRootObject": "index.html",
    "Enabled": true,
    "HttpVersion": "http2and3",
    "IsIPV6Enabled": true,
    "Logging": {
      "Bucket": "",
      "Enabled": false,
      "IncludeCookies": false,
      "Prefix": ""
    },
    "OriginGroups": {
      "Quantity": 0
    },
    "Origins": {
      "Items": [
        {
          "ConnectionAttempts": 3,
          "ConnectionTimeout": 10,
          "CustomHeaders": {
            "Quantity": 0
          },
          "CustomOriginConfig": {
            "HTTPPort": 80,
            "HTTPSPort": 443,
            "OriginKeepaliveTimeout": 5,
            "OriginProtocolPolicy": "http-only",
            "OriginReadTimeout": 30,
            "OriginSslProtocols": {
              "Items": [
                "TLSv1",
                "TLSv1.1",
                "TLSv1.2"
              ],
              "Quantity": 3
            }
          },
          "DomainName": "codeliver-io.s3-website-eu-west-1.amazonaws.com",
          "Id": "s3-website-codeliver-io",
          "OriginAccessControlId": "",
          "OriginPath": "",
          "OriginShield": {
            "Enabled": false
          }
        }
      ],
      "Quantity": 1
    },
    "PriceClass": "PriceClass_100",
    "Restrictions": {
      "GeoRestriction": {
        "Quantity": 0,
        "RestrictionType": "none"
      }
    },
    "Staging": false,
    "ViewerCertificate": {
      "ACMCertificateArn": "arn:aws:acm:us-east-1:957873067375:certificate/ee61922e-baa0-4653-b6d1-6ffb9000f448",
      "Certificate": "arn:aws:acm:us-east-1:957873067375:certificate/ee61922e-baa0-4653-b6d1-6ffb9000f448",
      "CertificateSource": "acm",
      "CloudFrontDefaultCertificate": false,
      "MinimumProtocolVersion": "TLSv1.2_2021",
      "SSLSupportMethod": "sni-only"
    },
    "WebACLId": ""
  },
  "ETag": "E1L7HSB0KD321P"
}
```

### Tags

```json
{
  "Tags": {
    "Items": []
  }
}
```
