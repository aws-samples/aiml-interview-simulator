# Interview Simulator - Backend

Production-ready serverless backend for the Interview Simulator application.

## Architecture

- **API Gateway**: REST API endpoints
- **Lambda Functions**: Serverless compute for processing
- **Step Functions**: Orchestrates video analysis workflow
- **S3**: Media file storage
- **DynamoDB**: Interview records storage
- **Amazon Transcribe**: Speech-to-text conversion
- **Amazon Bedrock**: AI-powered text analysis

## Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Python 3.9
- Node.js (for frontend integration)

## Quick Start

1. **Deploy the backend**:
   ```bash
   sam build
   sam deploy --guided
   ```

2. **Get the API endpoint**:
   ```bash
   aws cloudformation describe-stacks --stack-name interview-backend \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayEndpoint`].OutputValue' \
     --output text
   ```

3. **Update frontend configuration** with the API endpoint.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/upload` | Get presigned URL for video upload |
| GET | `/download` | Get presigned URL for video download |
| POST | `/record` | Create new interview record |
| GET | `/records` | List interview records |

## Processing Workflow

1. **Upload**: Video uploaded to S3 bucket
2. **Trigger**: S3 event triggers Step Functions
3. **Convert**: Video processing (currently simplified)
4. **Analyze**: Parallel video and audio analysis
5. **Store**: Results saved to DynamoDB

## Configuration

### Environment Variables

- `BUCKET`: S3 bucket for media files
- `TABLE_NAME`: DynamoDB table name
- `STATE_MACHINE_ARN`: Step Functions ARN

### Parameters

- `RecordsTableSecondaryIndex`: DynamoDB GSI name (default: `user_index`)

## Development

### Local Testing

```bash
# Start local API
sam local start-api

# Test specific function
sam local invoke ConvertVideoFunction -e events/s3-event.json
```

### Logs

```bash
# View all logs
sam logs --stack-name interview-backend --tail

# View specific function logs
sam logs -n ConvertVideoFunction --tail
```

## Deployment

### Production Deploy

```bash
sam build
sam deploy --parameter-overrides RecordsTableSecondaryIndex=user_index
```

### Clean Up

```bash
sam delete --stack-name interview-backend
```

## Monitoring

- **CloudWatch Logs**: Function execution logs
- **X-Ray Tracing**: Request tracing enabled
- **Step Functions**: Workflow execution history

## Security

- **IAM**: Least privilege access policies
- **S3**: CORS configured for web access
- **API Gateway**: CORS enabled
- **DynamoDB**: Encryption at rest

## Cost Optimization

- **DynamoDB**: Pay-per-request billing
- **Lambda**: Right-sized memory allocation
- **S3**: Lifecycle policies for old files

## Support

For issues:
1. Check CloudWatch logs
2. Review Step Functions execution
3. Validate IAM permissions
4. Test with minimal examples

## License

See main project LICENSE file.
