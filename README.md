# AWS-based Continuous Delivery for Hugo
By utilizing the AWS free tier, you can set up your own CD for your Hugo site, at no cost. Just follow the steps layed out below.

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
    "HUGO_BASE_URL": "https://mysite.com",
    "S3_BUCKET": "mysite-main-bucket"  
},
     "dev": {
        "HUGO_BASE_URL": "https://dev.mysite.com",
        "S3_BUCKET": "mysite-dev-bucket"  
    }
}
```
Values in the `branch_map.json` file will take precedence over values set in the env vars, in the case of a conflict between them.
## Logging
Default log level is set to `INFO`, in order to change it set the env var `LOG_LEVEL` in the lambda
function to any other valid python log level, such as `DEBUG`.