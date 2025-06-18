# Lambda MCP Server Demo (Streamable HTTP)

> **⚠️ IMPORTANT: The Lambda MCP Server module code IS maintained, just not in this repository. It is now hosted and maintained at [awslabs/mcp-lambda-handler](https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler).  This repository remains as sample code of how to use the module.**
>
> **To use the Lambda MCP Server, install the package directly from PyPI:**
>
> ```bash
> pip install awslabs.mcp_lambda_handler
> # or, if using uv:
> uv add awslabs.mcp_lambda_handler
> ```

> This server requires a client that supports Streamable HTTP (not SSE).  There are a few MCP clients that currently support Streamable HTTP including the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector).  There is also as a Streamable HTTP client included in this repo, built [Strands Agents](https://strandsagents.com/latest/).

This project demonstrates a powerful and developer-friendly way to create serverless [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) tools using [AWS Lambda](https://aws.amazon.com/lambda/?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code). It showcases how to build a stateless, serverless MCP server with minimal boilerplate and an excellent developer experience.

## the_context()

In an episode of [the_context](https://www.youtube.com/playlist?list=PLeAh2CQypN9V8E-pkG6ZAXj-w3dgy1qQn), Tiffany Souterre and Mike discussed streamable HTTP for MCP as well as running (an older version of) this project:

<p align="center">
  <a href="https://youtu.be/Ejua5LQTqek">
    <img src="thumb.png" alt="MCP - Can Lambda do it? - Streamable HTTP Model Context Protocol" width="600" /><br>
  </a>
</p>

## Example

Here is the minimal code to get an MCP server running in an AWS Lambda function:

```python
from awslabs.mcp_lambda_handler import MCPLambdaHandler

mcp_server = MCPLambdaHandler(name="mcp-lambda-server", version="1.0.0")

@mcp_server.tool()
def get_time() -> str:
    from datetime import datetime, UTC
    return datetime.now(UTC).isoformat()

def lambda_handler(event, context):
    return mcp_server.handle_request(event, context)
```

## Session State Management

The Lambda MCP Server includes built-in session state management that persists across tool invocations within the same conversation. This is particularly useful for tools that need to maintain context or share data between calls.

Session data is stored in a DynamoDB table against a sessionId key. This is all managed for you.

Here's an example of how to use session state:

```Python
from lambda_mcp.lambda_mcp import LambdaMCPServer

session_table = os.environ.get('MCP_SESSION_TABLE', 'mcp_sessions')

mcp_server = LambdaMCPServer(name="mcp-lambda-server", version="1.0.0", session_store=session_table)

@mcp_server.tool()
def increment_counter() -> int:
    """Increment a session-based counter."""
    # Get the current counter value from session state, default to 0 if not set
    counter = mcp_server.session.get('counter', 0)
    
    # Increment the counter
    counter += 1
    
    # Store the new value in session state
    mcp_server.session['counter'] = counter
    
    return counter

@mcp_server.tool()
def get_counter() -> int:
    """Get the current counter value."""
    return mcp_server.session.get('counter', 0)
```

The session state is automatically managed per conversation and persists across multiple tool invocations. This allows you to maintain stateful information without needing additional external storage, while still keeping your Lambda function stateless.

## Authentication

The sample server stack uses Bearer token authentication via an Authorization header, which is compliant with the MCP standard. This provides a basic level of security for your MCP server endpoints. Here's what you need to know:

1. **Bearer Token**: When you deploy the stack, a bearer token is configured through a custom authorizer in API Gateway
2. **Using the Bearer Token**: 
   - The client must include the bearer token in requests using the `Authorization` header with the format: `Bearer <your-token>`
   - The token value is provided in the stack outputs after deployment
   - The sample client is configured to automatically include this header when provided with the token

3. **Custom Authorizer**: The implementation uses a simple custom authorizer that validates a single bearer token. This can be easily extended or replaced with more sophisticated authentication systems like Amazon Cognito for production use.

⚠️ **Security Note**: While bearer token authentication provides a standard-compliant authentication mechanism, consider implementing additional security measures such as:
- AWS IAM roles and policies
- OAuth 2.0 / JWT with proper token management
- Amazon Cognito User Pools

The current bearer token implementation is primarily intended for demonstration and development purposes. For production systems handling sensitive data, implement appropriate additional security measures based on your specific requirements.

## What is this all about?

This is a proof-of-concept implementation of an MCP server running on AWS Lambda, along with a Strands Agents client that demonstrates its functionality. The project consists of two main components:

1. **Lambda MCP Server**: A Python-based serverless implementation that makes it incredibly simple to deploy cloud hosted MCP tools.
2. **Strands Agents Client**: A demonstration client that shows how to interact with the Lambda MCP server using Strands Agents.

## Example Tools

The server comes with three example tools that demonstrate different use cases:

1. `get_weather(city: str)`: Get the current weather for a city. Returns a simulated temperature for the given city.
2. `count_s3_buckets()`: Count the number of S3 buckets in your AWS account.
3. `get_time()`: Get the current UTC date and time, and show how long since last time was asked for (if session available).

## Getting Started

### Prerequisites

- [AWS Account](https://aws.amazon.com/free/?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) with appropriate permissions
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) installed
- Access to [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) in your AWS account
- [Amazon Nova Pro](https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) enabled in your Amazon Bedrock model access settings

### Amazon Bedrock Setup

Before running the client, ensure you have:

1. [Enabled Amazon Bedrock access](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) in your AWS account
2. [Enabled the Amazon Nova Models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) in your Bedrock model access settings
3. Appropriate [IAM permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) to invoke Bedrock APIs

### Server Deployment

1. Clone this repository:
   ```bash
   git clone <repository-url>
   ```

1. Navigate to the server directory:
   ```bash
   cd server-http-python-lambda
   ```

1. Deploy using SAM:
   ```bash
   sam build && sam deploy --guided
   ```

   Note: You will be prompted for an `McpAuthToken`.  This is the Authorization Bearer token that will be requitred to call the endpoint. This simple implimentation uses an [AWS API Gateway authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) with the `McpAuthToken` passed in as an env var.  This can be swapped out for a production implimentation as required. 

### Client Setup

1. Update the `api_gateway_url` and `auth_token` in `./client-strands-agents-mcp/main.py`:
   ```bash
   cd client-strands-agents-mcp
   ```

1. Navigate to the client directory:
   ```bash
   cd client-strands-agents-mcp
   ```

1. Run the helper script:
   ```bash
   uv sync
   uv run main.py
   ```

## Adding New Tools

The Lambda MCP Server is designed to make tool creation as simple as possible. Here's how to add a new tool:

1. Open `server/app.py`
2. Add your new tool using the decorator pattern:

```python
@mcp_server.tool()
def my_new_tool(param1: str, param2: int) -> str:
    """Your tool description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Your tool implementation
    return f"Processed {param1} with value {param2}"
```

That's it! The decorator handles:
- Type validation
- Request parsing
- Response formatting
- Error handling
- MCP Documentation generation

## Notes

- For production use, consider adding authentication and authorization using [AWS IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

For AWS security best practices, refer to the [AWS Security Documentation](https://docs.aws.amazon.com/security/?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code) and [Amazon Bedrock security best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html?trk=64e03f01-b931-4384-846e-db0ba9fa89f5&sc_channel=code).

## License

This library is licensed under the [MIT-0 License](https://github.com/aws/mit-0). See the LICENSE file.

## Changes

### Version 2.0.0
- The Lambda MCP Server module code is no longer included in this repository; it is now maintained at [awslabs/mcp-lambda-handler](https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler).
- Updated installation instructions to use the PyPI package: `pip install awslabs.mcp_lambda_handler` or `uv add awslabs.mcp_lambda_handler`.
- README example code now uses the new package import and shows a minimal Lambda MCP server example.
- Updated the list and descriptions of example tools to match the current implementation in `app.py`.
- Updated client instructions to use Strands Agents and removed references to the TypeScript client.
- Updated prerequisites and deployment instructions for clarity and accuracy.
- Improved documentation for session state management and authentication.
- Various documentation and usability improvements throughout the README.

### Version 1.1.0
- Replaced API Key authentication with Bearer token authentication via Authorization header
- Added custom authorizer to API Gateway for token validation
- Updated client configuration to use bearer tokens
- Made authentication system compliant with MCP standard
- Added this change log section

### Version 1.0.0
- Initial release
- Basic MCP server implementation with AWS Lambda
- Session state management with DynamoDB
- Example tools implementation
- TypeScript HTTP client with Amazon Bedrock integration
