#!/bin/bash

# Interview Simulator Infrastructure Migration Script
# This script helps migrate from the original template to the updated infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="interview-backend"
REGION="us-east-1"
BACKUP_DIR="./backup-$(date +%Y%m%d-%H%M%S)"

echo -e "${BLUE}🚀 Interview Simulator Infrastructure Migration${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check SAM CLI
    if ! command -v sam &> /dev/null; then
        print_error "SAM CLI not found. Please install SAM CLI."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Backup current infrastructure
backup_current_state() {
    print_info "Creating backup of current infrastructure..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup CloudFormation stack
    aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" > "$BACKUP_DIR/stack-description.json" 2>/dev/null || true
    
    # Backup current template
    cp template.yaml "$BACKUP_DIR/template-original.yaml" 2>/dev/null || true
    
    # Backup Lambda function code
    mkdir -p "$BACKUP_DIR/lambda-functions"
    
    # Get function names from stack
    FUNCTIONS=$(aws cloudformation describe-stack-resources --stack-name "$STACK_NAME" --region "$REGION" --query 'StackResources[?ResourceType==`AWS::Lambda::Function`].PhysicalResourceId' --output text 2>/dev/null || echo "")
    
    if [ -n "$FUNCTIONS" ]; then
        for func in $FUNCTIONS; do
            print_info "Backing up function: $func"
            aws lambda get-function --function-name "$func" --region "$REGION" > "$BACKUP_DIR/lambda-functions/$func.json" 2>/dev/null || true
        done
    fi
    
    print_status "Backup created in $BACKUP_DIR"
}

# Validate current deployment
validate_current_deployment() {
    print_info "Validating current deployment..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackStatus' --output text)
        print_info "Current stack status: $STACK_STATUS"
        
        if [[ "$STACK_STATUS" != "CREATE_COMPLETE" && "$STACK_STATUS" != "UPDATE_COMPLETE" ]]; then
            print_warning "Stack is not in a stable state. Status: $STACK_STATUS"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        print_error "Stack $STACK_NAME not found in region $REGION"
        exit 1
    fi
    
    print_status "Current deployment validated"
}

# Update template
update_template() {
    print_info "Updating infrastructure template..."
    
    # Backup current template
    cp template.yaml template-backup-$(date +%Y%m%d-%H%M%S).yaml
    
    # Copy updated template
    if [ -f "template-updated.yaml" ]; then
        cp template-updated.yaml template.yaml
        print_status "Template updated to latest version"
    else
        print_error "template-updated.yaml not found"
        exit 1
    fi
}

# Deploy updated infrastructure
deploy_infrastructure() {
    print_info "Deploying updated infrastructure..."
    
    # Build the application
    print_info "Building SAM application..."
    sam build
    
    # Deploy with parameters
    print_info "Deploying to AWS..."
    sam deploy \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --parameter-overrides \
            EnableFFmpegLayer=false \
        --capabilities CAPABILITY_IAM \
        --no-confirm-changeset \
        --no-fail-on-empty-changeset
    
    print_status "Infrastructure deployment completed"
}

# Validate deployment
validate_deployment() {
    print_info "Validating updated deployment..."
    
    # Check stack status
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackStatus' --output text)
    
    if [[ "$STACK_STATUS" == "UPDATE_COMPLETE" || "$STACK_STATUS" == "CREATE_COMPLETE" ]]; then
        print_status "Stack deployment successful"
    else
        print_error "Stack deployment failed. Status: $STACK_STATUS"
        exit 1
    fi
    
    # Get API endpoint
    API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayEndpoint`].OutputValue' --output text 2>/dev/null || echo "Not found")
    
    if [ "$API_ENDPOINT" != "Not found" ]; then
        print_status "API Gateway endpoint: $API_ENDPOINT"
    fi
    
    # Test API endpoint
    if [ "$API_ENDPOINT" != "Not found" ]; then
        print_info "Testing API endpoint..."
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_ENDPOINT}records" || echo "000")
        
        if [ "$HTTP_STATUS" -eq 200 ]; then
            print_status "API endpoint is responding"
        else
            print_warning "API endpoint returned status: $HTTP_STATUS"
        fi
    fi
}

# Test Step Functions
test_step_functions() {
    print_info "Testing Step Functions..."
    
    # Get State Machine ARN
    STATE_MACHINE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`StateMachineArn`].OutputValue' --output text 2>/dev/null || echo "Not found")
    
    if [ "$STATE_MACHINE_ARN" != "Not found" ]; then
        print_status "State Machine ARN: $STATE_MACHINE_ARN"
        
        # Check recent executions
        RECENT_EXECUTIONS=$(aws stepfunctions list-executions --state-machine-arn "$STATE_MACHINE_ARN" --region "$REGION" --max-items 1 --query 'executions[0].status' --output text 2>/dev/null || echo "None")
        
        if [ "$RECENT_EXECUTIONS" != "None" ]; then
            print_info "Most recent execution status: $RECENT_EXECUTIONS"
        fi
    fi
}

# Generate summary report
generate_summary() {
    print_info "Generating migration summary..."
    
    SUMMARY_FILE="$BACKUP_DIR/migration-summary.txt"
    
    cat > "$SUMMARY_FILE" << EOF
Interview Simulator Infrastructure Migration Summary
==================================================

Migration Date: $(date)
Stack Name: $STACK_NAME
Region: $REGION
Backup Location: $BACKUP_DIR

Changes Applied:
- Updated Python runtime from 3.8 to 3.9
- Added FFmpeg layer conditional support
- Enhanced error handling in UpdateTableFunction
- Fixed DynamoDB Decimal type conversion
- Improved timeout and memory configurations
- Changed DynamoDB to pay-per-request billing

Stack Outputs:
EOF
    
    # Add stack outputs to summary
    aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs' --output table >> "$SUMMARY_FILE" 2>/dev/null || echo "Could not retrieve stack outputs" >> "$SUMMARY_FILE"
    
    print_status "Migration summary saved to $SUMMARY_FILE"
}

# Main execution
main() {
    echo
    print_info "Starting infrastructure migration process..."
    echo
    
    # Confirm migration
    print_warning "This will update your infrastructure. Make sure you have:"
    echo "  1. Tested the changes in a development environment"
    echo "  2. Reviewed the updated template"
    echo "  3. Have necessary permissions"
    echo
    read -p "Continue with migration? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Migration cancelled"
        exit 0
    fi
    
    # Execute migration steps
    check_prerequisites
    backup_current_state
    validate_current_deployment
    update_template
    deploy_infrastructure
    validate_deployment
    test_step_functions
    generate_summary
    
    echo
    print_status "🎉 Migration completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Update your frontend API endpoint if needed"
    echo "  2. Test the application with real video uploads"
    echo "  3. Monitor CloudWatch logs for any issues"
    echo "  4. Follow FFMPEG_LAYER_GUIDE.md for full video processing"
    echo
    print_info "Backup and summary available in: $BACKUP_DIR"
}

# Handle script interruption
trap 'print_error "Migration interrupted"; exit 1' INT TERM

# Run main function
main "$@"
