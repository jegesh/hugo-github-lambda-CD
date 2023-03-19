# AWS-based Continuous Delivery for Hugo
By utilizing the AWS free tier, you can set up your own CD for your Hugo site, at no cost. Just follow the steps layed out below.

## Prerequisites
 1. A Hugo project
 2. A git repo on Github with the project code (additional git servers may be supported in the future)
 3. An AWS account (with sufficient permissions to Lambda, S3, ECR, and IAM)
 4. Docker installed locally
 5. The AWS CLI installed on your development machine

## Setup
 2. Go over the CloudFormation template file (`hugo-builder-stack.json` in the root of this repo) and make necessary changes (detailed below)
 3. Run `aws cloudformation deploy --template-file hugo-builder-stack.json --stack-name hugo-builder --region my-chosen-region`
 4. Add a `branch_map.json` file to your repo if desired (see below)
 5. Find the Lambda invocation url (in the `Function Overview` section of the Lambda console) and add it as a webhook to your Github repo
 6. Upload your application code (without the `public/` dir) to your
 7. Your site should be deployed at the url you set in the bucket settings in the CloudFormation template!
## Configuration
The following environment variables can be set on the Lambda function in order to control the various stages
of the build process. These env vars are mandatory:  
 - `GITHUB_USERNAME`
 - `GITHUB_ACCESS_TOKEN`
 - `HUGO_BASE_URL`
 - `S3_BUCKET` - just the bucket name
 - `BRANCH_NAME` - name of branch to build from. pushes from all other branches will be ignored (see below how to allow multiple branches)
 
Optionally you can also set:  
  - `HUGO_CMD_FLAGS` - additional flags for the Hugo build command
 
 #### Config per Branch
 The env vars `HUGO_BASE_URL` and `S3_BUCKET` can alternatively be set in a file named `branch_map.json` that needs to 
 be in the root of the repo. This allows for building off of multiple branches with differing destination buckets. For instance:  
 ```json
{
  "master": {
    "HUGO_BASE_URL": "https://www.mysite.com",
    "S3_BUCKET": "www.mysite.com"  
},
     "dev": {
        "HUGO_BASE_URL": "https://dev.mysite.com",
        "S3_BUCKET": "dev.mysite.com"  
    }
}
```
Values in the `branch_map.json` file will take precedence over values set in the env vars, in the case of a conflict between them.
## Logging
Default log level is set to `INFO`, in order to change it set the env var `LOG_LEVEL` in the lambda
function to any other valid python log level, such as `DEBUG`.

## Additional Configurations
### DNS - General
[See here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/VirtualHosting.html#VirtualHostingCustomURLs) for general instructions.
### SSL
#### Cloudflare
If you're using Cloudflare to manage DNS for your website, refer to [this](https://support.cloudflare.com/hc/en-us/articles/360037983412-Configuring-an-Amazon-Web-Services-static-site-to-use-Cloudflare)
document for setup instructions. Other DNS management services will require a different own set of IP addresses in the bucket policy.

#### Cloudfront
To use a native AWS service to add security to your site, [this](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/getting-started-secure-static-website-cloudformation-template.html) is what you need.

## A Note about Costs
All the AWS services deployed in this scenario will be free of charge under the general (unlimited) AWS Free Tier. If you already have
other services utilizing the free tier (e.g. ECR storage is free up to 500MB - the builder image weighs just under 400MB), you may end up going over the allowed quota and receive a very small bill at the end of the month for 
the additional usage.