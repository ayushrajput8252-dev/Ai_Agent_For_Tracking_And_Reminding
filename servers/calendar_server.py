from mcp.server import Server
from mcp import types
from auth.credentials import CREDENTIALS
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

server = Server("calendar-server")

def get_calendar_service():
    """Returns an authenticated Google Calendar service."""
    creds_data = CREDENTIALS["calendar"]
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("calendar", "v3", credentials=creds)

@server.list_tools()
async def list_tools() -> list[types.tools]:
    return [
        types.Tool(
            name="create_event",
            description="Create a calendar event",
            inputSchema={
                "type" : "object",
                "properties": {
                    "title" : {"type":"string"},
                    "date": {"type":"string", "description": "YYYY-MM-DD"},
                    "time":   {"type": "string", "description": "HH:MM"},
                    "time":   {"type": "string", "description": "HH:MM"},
                    "duration_mins": {"type": "integer", "default": 60},
                },
                "required": ["title", "date", "time"],
            },
        ),
        types.Tool(
            name = "list_events",
            description="List upcoming calendar events",
            inputSchema={
                "type": "object",
                "properties" : {
                    "days_ahead" : {"type":"integer", "default" : 7}
                },
            },
        ),
    ]

@server.call_tool()
async def call_tool(name:str, arguments: dict) -> list[types.TextContent]:
    service = get_calendar_service()

    if name == "create_event":
        from datetime import datetime, timedelta
        date = arguments["date"]
        time = arguments["time"]

        start = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
        duration = arguments.get("duration_mins", 60)
        end = start + timedelta(minutes=duration)

        #event data
        event_data = {
            "summary" : arguments["title"],
            "start" : {"dateTime" : start.isoformat()},
            "end" : {"dateTime" : end.isoformat()}
        }
        #create event
        event = service.events().insert(
            calendarId = "primary",
            body = event_data
        ).execute()

        return [
           types.TextContent(
               type="text",
               text=f"Event created: {event['htmlLink']}"
           )
        ]  
    
    elif name == "list_events":
        return [
            types.TextContent(
                types="text",
                text="Upcoming: Team standup Tue 9am, Lunch Wed 12pm"
            )
        ]
