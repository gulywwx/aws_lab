# Cloudfront s3 static website
This solution creates a CloudFront distribution to serve your website to viewers. The distribution is configured with a CloudFront origin access identity to make sure that the website is only accessible via CloudFront, not directly from S3.

1. Run the following command to create the CloudFormation stack
    ```shell
    aws cloudformation deploy --template-file template.yaml --stack-name mystaticwebsite-cloudfront-distribution
    ```

2. Run the following command to retrieve the CloudFront distribution domain
    ```shell
    aws cloudformation describe-stacks --stack-name mystaticwebsite-cloudfront-distribution
    ```

3. Take note of the OutputValue of "OutputKey": "DistributionDomainName" and "OutputKey": "StaticResourcesBucketName".

4. Run the following command to create a file name index.html and upload it to the S3 bucket
    ```shell
    aws s3 cp index.html s3://<static resources bucket name>
    ```

5. Request the CloudFront URL taken from the stack output to see the content returned from CloudFront
    ```shell
    curl https://<cloudfront distribution domain>
    ```
