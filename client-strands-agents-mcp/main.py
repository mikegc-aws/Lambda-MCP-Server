from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Add your API Gateway URL here as it outputs from the sam deploy command (include /mcp at the end):
api_gateway_url = "https://1234567890.execute-api.us-east-1.amazonaws.com/Prod/mcp"
auth_token = "1234567890"

# This uses the Nova Pro model from Amazon Bedrock, in a US region:
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
)

shttp_mcp_client = MCPClient(lambda: streamablehttp_client(
        url=api_gateway_url, 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
)

# Create an agent with MCP tools
with shttp_mcp_client:

    # Get the tools from the MCP server
    mcp_tools = shttp_mcp_client.list_tools_sync()

    # Create an agent with these tools
    agent = Agent(
        model=bedrock_model,
        tools=mcp_tools
    )

    # Simple CLI chat interface
    print("Chat with the agent (press Ctrl+C to exit)")
    print("----------------------------------------")
    
    while True:
        try:
            user_input = input("\n\n> ").strip()
            if user_input:  # Only process non-empty input
                agent(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break