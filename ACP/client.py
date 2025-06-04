import asyncio
from acp_sdk import Message, MessagePart, MessagePartEvent, MessageCompletedEvent, GenericEvent
from acp_sdk.client import Client

async def run_client():
    async with Client(base_url="http://localhost:8000") as client:
        user_request = "Book me a trip to Paris for next weekend."
        user_message_input = Message(parts=[MessagePart(content=user_request)])
        
        print("Sending request to trip_planning_coordinator...")
        async for event in client.run_stream(agent="trip_planning_coordinator", input=[user_message_input]):
            if isinstance(event, MessagePartEvent):
                print(event.part.content)
            elif isinstance(event, MessageCompletedEvent):
                print("\n✅ Completed.\n")
            elif isinstance(event, GenericEvent):
                print("\nℹ️ Generic Event:")
                for key, value in event.generic.model_dump().items():
                    print(f"{key}: {value}")
            else:
                print(f"⚠️ Unhandled event type: {event}")

if __name__ == "__main__":
    asyncio.run(run_client())