from awslabs.mcp_lambda_handler import MCPLambdaHandler
from datetime import datetime, UTC
import random
import boto3
import os

# Get session table name from environment variable
session_table = os.environ.get('MCP_SESSION_TABLE', 'mcp_sessions')

# Create the MCP server instance
mcp_server = MCPLambdaHandler(name="mcp-lambda-server", version="1.0.0", session_store=session_table)

@mcp_server.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a city.
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        A string describing the weather
    """
    temp = random.randint(15, 35)
    return f"The temperature in {city} is {temp}°C"

@mcp_server.tool()
def count_s3_buckets() -> int:
    """Count the number of S3 buckets."""
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    return len(response['Buckets'])

@mcp_server.tool()
def get_time() -> str:
    """Get the current UTC date and time, and show how long since last time was asked for (if session available)."""
    try:
        # Get the current UTC time as a datetime object and formatted string
        now = datetime.now(UTC)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Retrieve the session object if available
        session = mcp_server.get_session()
        # Get the last time the user asked for the time from the session (if any)
        last_time = session.get('last_time_asked') if session else None
        last_time_str = last_time if last_time else None
        seconds_since = None

        # If there was a previous time, calculate how many seconds have passed
        if last_time:
            try:
                last_time_dt = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                seconds_since = int((now - last_time_dt).total_seconds())
            except Exception:
                # If parsing fails, just skip the seconds_since calculation
                seconds_since = None

        # Store the current time as the new 'last_time_asked' in the session
        if session:
            def update_last_time(s):
                s.set('last_time_asked', now_str)
            mcp_server.update_session(update_last_time)

        # Build the response string
        response = f"Current UTC time: {now_str}"
        if last_time_str:
            response += f"\nLast time asked: {last_time_str}"
            if seconds_since is not None:
                response += f"\nSeconds since last time: {seconds_since}"
        return response
    
    except Exception as e:
        # Catch-all for unexpected errors
        return f"Error: An unexpected error occurred: {str(e)}"

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    return mcp_server.handle_request(event, context) 