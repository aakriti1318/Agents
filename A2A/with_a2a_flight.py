import asyncio
import platform
from crewai import Agent, Task, Crew
from datetime import datetime, timedelta
import json

# Mock data simulating external API responses (no real network calls)
MOCK_FLIGHTS = {"Paris": {"date": "2025-06-06", "time": "10:00 AM", "flight": "AF123", "price": 300}}
MOCK_HOTELS = {"Paris": {"check_in": "2025-06-06", "nights": 2, "hotel": "Hotel Paris", "price": 200}}
MOCK_WEATHER = {"Paris": {"date": "2025-06-06", "forecast": "Sunny, 75°F"}}

# Simulate A2A Agent Card (JSON metadata for discovery and capability exchange)
def create_agent_card(agent_name, capabilities, endpoint):
    return {
        "agent_name": agent_name,
        "capabilities": capabilities,
        "endpoint": endpoint,
        "authentication": {"scheme": "Bearer", "token": f"mock-token-{agent_name}"}
    }

# Simulate A2A message structure (JSON-RPC 2.0 format)
def create_a2a_message(sender, receiver, method, params, task_id):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": task_id,
        "role": "agent",
        "sender": sender,
        "receiver": receiver
    }

# Define Agents with A2A-inspired collaboration
client_agent = Agent(
    role="Client Agent",
    goal="Interpret user request and coordinate trip planning for Paris next weekend using A2A protocol",
    backstory="A helpful assistant that uses A2A to delegate tasks to specialized agents.",
    verbose=True
)

flight_agent = Agent(
    role="Flight Agent",
    goal="Find and 'book' flights to a destination for given dates via A2A communication",
    backstory="An expert in flight schedules, using A2A to share flight data.",
    verbose=True
)

hotel_agent = Agent(
    role="Hotel Agent",
    goal="Find and 'book' hotels for given dates and location, using flight arrival from A2A",
    backstory="A specialist in hotel reservations, collaborating via A2A.",
    verbose=True
)

weather_agent = Agent(
    role="Weather Agent",
    goal="Provide weather forecast for a destination and date via A2A requests",
    backstory="A meteorology expert supporting travel plans with A2A.",
    verbose=True
)

# Simulate A2A Agent Cards for discovery
agent_cards = {
    "flight_agent": create_agent_card("flight_agent", ["find_flight", "book_flight"], "/flight_endpoint"),
    "hotel_agent": create_agent_card("hotel_agent", ["find_hotel", "book_hotel"], "/hotel_endpoint"),
    "weather_agent": create_agent_card("weather_agent", ["get_forecast"], "/weather_endpoint")
}

# Define Tasks with A2A-style communication
async def client_task_func():
    task_id = "task-001"
    user_request = "Book me a trip to Paris for next weekend."
    
    # Simulate A2A capability discovery via Agent Cards
    flight_capable = "find_flight" in agent_cards["flight_agent"]["capabilities"]
    hotel_capable = "find_hotel" in agent_cards["hotel_agent"]["capabilities"]
    weather_capable = "get_forecast" in agent_cards["weather_agent"]["capabilities"]
    
    # A2A request to Flight Agent
    if flight_capable:
        flight_msg = create_a2a_message("client_agent", "flight_agent", "find_flight", 
                                        {"destination": "Paris", "date": "2025-06-06"}, task_id)
        flight_response = MOCK_FLIGHTS["Paris"]
    
    # A2A request to Hotel Agent, sharing flight arrival time
    if hotel_capable and flight_response:
        hotel_msg = create_a2a_message("client_agent", "hotel_agent", "book_hotel", 
                                       {"destination": "Paris", "check_in": "2025-06-06", "nights": 2, 
                                        "flight_arrival": flight_response["time"]}, task_id)
        hotel_response = MOCK_HOTELS["Paris"]
    
    # A2A request to Weather Agent
    if weather_capable:
        weather_msg = create_a2a_message("client_agent", "weather_agent", "get_forecast", 
                                         {"destination": "Paris", "date": "2025-06-06"}, task_id)
        weather_response = MOCK_WEATHER["Paris"]
    
    # Compile trip plan
    plan = (f"Trip Plan for Paris:\n"
            f"- Flight booked: {flight_response['flight']} on {flight_response['date']} at {flight_response['time']}, ${flight_response['price']}\n"
            f"- Hotel booked: {hotel_response['hotel']} on {hotel_response['check_in']} for {hotel_response['nights']} nights, ${hotel_response['price']}, check-in ready after flight at {flight_response['time']}\n"
            f"- Weather forecast: {weather_response['date']}, {weather_response['forecast']}")
    return plan

client_task = Task(
    description="Interpret user request: 'Book me a trip to Paris for next weekend.' Use A2A protocol to coordinate flight, hotel, and weather info.",
    agent=client_agent,
    async_execution=True, 
    expected_output="A coordinated trip plan for Paris with flight, hotel, and weather details.",
    function=client_task_func
)

flight_task = Task(
    description="Respond to A2A request: Find a flight to Paris for 2025-06-06. Return flight number, date, time, and price.",
    agent=flight_agent,
    async_execution=False,  
    expected_output="Flight details: flight number, date, time, and price."
)

hotel_task = Task(
    description="Respond to A2A request: Book a hotel in Paris for check-in 2025-06-06, 2 nights, using flight arrival time. Return hotel name, check-in date, nights, and price.",
    agent=hotel_agent,
    async_execution=False,  
    expected_output="Hotel details: hotel name, check-in date, nights, and price."
)

weather_task = Task(
    description="Respond to A2A request: Get weather forecast for Paris for 2025-06-06. Return date and forecast.",
    agent=weather_agent,
    async_execution=False,  
    expected_output="Weather forecast: date and conditions."
)

# Create Crew with A2A-inspired collaboration
crew = Crew(
    agents=[client_agent, flight_agent, hotel_agent, weather_agent],
    tasks=[client_task, flight_task, hotel_task, weather_task], 
    verbose=True
)
# Main execution
async def main():
    print("=== Trip Planning with A2A Protocol ===")
    # Simulate A2A agent discovery
    print("Agent Cards for Discovery:")
    print(json.dumps(agent_cards, indent=2))
    print("\nRunning trip planning...")
    result = await crew.kickoff_async()
    print("\nFinal Trip Plan:")
    print(result)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())