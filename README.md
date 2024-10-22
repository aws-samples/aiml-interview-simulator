# Interview Mentorship

This repository is part of the interview simulation solution prototype.

## Architecture

![Architecture](./assets/wpt-architecture.png)

## Prerequisites

It is recommended to run this prototype in a sandbox account. The prototype does not have tests, and not all security best practices are implemented.

To deploy the solution, you will need:

- [AWS CLI](https://docs.aws.amazon.com/pt_br/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Region _us-east-1_
- Node.js v18.16.0, NPM v9.5.1, Python v3.8.8

## Getting Started

1. Deploy the [backend](./backend/README.md)
2. Change [API endpoint](./frontend/src/services/api.js)
3. Deploy [frontend](./frontend/README.md)

## Disclaimer

Sample code, software libraries, command line tools, proofs of concept, templates, or other related technology are provided as AWS Content or Third-Party Content under the AWS Customer Agreement, or the relevant written agreement between you and AWS (whichever applies). You should not use this AWS Content or Third-Party Content in your production accounts, or on production or other critical data. You are responsible for testing, securing, and optimizing the AWS Content or Third-Party Content, such as sample code, as appropriate for production grade use based on your specific quality control practices and standards. Deploying AWS Content or Third-Party Content may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.
