import asyncio
from acp_sdk import Message, MessagePart, GenericEvent
from acp_sdk.server import Context, Server
from crewai import Agent, Task, Crew
import json

# Mock data simulating external API responses
MOCK_FLIGHTS = {"Paris": {"date": "2025-06-06", "time": "10:00 AM", "flight": "AF123", "price": 300}}
MOCK_HOTELS = {"Paris": {"check_in": "2025-06-06", "nights": 2, "hotel": "Hotel Paris", "price": 200}}
MOCK_WEATHER = {"Paris": {"date": "2025-06-06", "forecast": "Sunny, 75°F"}}

server = Server()

@server.agent("trip_planning_coordinator")
async def trip_planning_coordinator(input: list[Message], context: Context):
    """Coordinates trip planning for Paris using ACP protocol"""
    # Extract user request from the last message
    user_request = input[-1].parts[0].content
    yield MessagePart(content=f"Processing request: {user_request}\n")

    # Define Agents
    client_agent = Agent(
        role="Client Agent",
        goal="Coordinate trip planning for Paris using ACP protocol",
        backstory="A helpful assistant that delegates tasks via ACP.",
        verbose=True
    )

    flight_agent = Agent(
        role="Flight Agent",
        goal="Find and book flights via ACP communication",
        backstory="An expert in flight schedules, using ACP to share data.",
        verbose=True
    )

    hotel_agent = Agent(
        role="Hotel Agent",
        goal="Book hotels using flight arrival from ACP",
        backstory="A specialist in hotel reservations, collaborating via ACP.",
        verbose=True
    )

    weather_agent = Agent(
        role="Weather Agent",
        goal="Provide weather forecast via ACP requests",
        backstory="A meteorology expert supporting travel plans with ACP.",
        verbose=True
    )

    # Simulate capability discovery (mocked for simplicity)
    capabilities = {
        "flight_agent": ["find_flight", "book_flight"],
        "hotel_agent": ["find_hotel", "book_hotel"],
        "weather_agent": ["get_forecast"]
    }

    # Client task logic
    async def client_task_func():
        task_id = "task-001"
        flight_capable = "find_flight" in capabilities["flight_agent"]
        hotel_capable = "find_hotel" in capabilities["hotel_agent"]
        weather_capable = "get_forecast" in capabilities["weather_agent"]

        # Request to Flight Agent
        if flight_capable:
            yield MessagePart(content="Requesting flight details...\n")
            flight_response = MOCK_FLIGHTS["Paris"]
        
        # Request to Hotel Agent, sharing flight arrival
        if hotel_capable and flight_response:
            yield MessagePart(content="Requesting hotel booking...\n")
            hotel_response = MOCK_HOTELS["Paris"]
        
        # Request to Weather Agent
        if weather_capable:
            yield MessagePart(content="Requesting weather forecast...\n")
            weather_response = MOCK_WEATHER["Paris"]
        
        # Compile trip plan
        plan = (f"Trip Plan for Paris:\n"
                f"- Flight booked: {flight_response['flight']} on {flight_response['date']} at {flight_response['time']}, ${flight_response['price']}\n"
                f"- Hotel booked: {hotel_response['hotel']} on {hotel_response['check_in']} for {hotel_response['nights']} nights, ${hotel_response['price']}, check-in ready after flight at {flight_response['time']}\n"
                f"- Weather forecast: {weather_response['date']}, {weather_response['forecast']}")
        yield MessagePart(content=plan)

    # Define Tasks
    client_task = Task(
        description="Coordinate trip to Paris using ACP protocol.",
        agent=client_agent,
        async_execution=True,
        expected_output="A coordinated trip plan for Paris.",
        function=client_task_func
    )

    flight_task = Task(
        description="Find a flight to Paris for 2025-06-06.",
        agent=flight_agent,
        async_execution=False,
        expected_output="Flight details."
    )

    hotel_task = Task(
        description="Book a hotel in Paris for 2025-06-06, 2 nights.",
        agent=hotel_agent,
        async_execution=False,
        expected_output="Hotel details."
    )

    weather_task = Task(
        description="Get weather forecast for Paris for 2025-06-06.",
        agent=weather_agent,
        async_execution=False,
        expected_output="Weather forecast."
    )

    # Create Crew
    crew = Crew(
        agents=[client_agent, flight_agent, hotel_agent, weather_agent],
        tasks=[client_task, flight_task, hotel_task, weather_task],
        verbose=True
    )

    yield MessagePart(content="Starting trip planning with ACP crew...\n")
    
    try:
        result = await crew.kickoff_async()
        yield MessagePart(content=result.raw)
    except Exception as e:
        yield MessagePart(content=f"Error during planning: {str(e)}")

if __name__ == "__main__":
    server.run()