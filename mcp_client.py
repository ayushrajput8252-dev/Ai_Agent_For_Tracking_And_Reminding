# mcp_client.py — connects your agent to all MCP servers
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def get_all_tools():
    """
    Start all MCP servers and return a combined list of LangChain tools.
    Each server runs as a subprocess — clean and isolated.
    """
    all_tools = []
    
    server = [
        StdioServerParameters(command="python", args=["server/emai_server.py"]),
        StdioServerParameters(command="python", args=["servers/calendar_server.py"]),
    ]
    #now start each server 
    for server_params in server:
        #start each subproccess
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools() # converts MCP tools → LangChain tools
                all_tools.extend(tools)

    return all_tools