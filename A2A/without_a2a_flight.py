import asyncio
import platform
from crewai import Agent, Task, Crew
from datetime import datetime, timedelta

# Mock data for simplicity (no real booking or API calls)
MOCK_FLIGHTS = {"Paris": {"date": "2025-06-06", "time": "10:00 AM", "flight": "AF123", "price": 300}}
MOCK_HOTELS = {"Paris": {"check_in": "2025-06-06", "nights": 2, "hotel": "Hotel Paris", "price": 200}}
MOCK_WEATHER = {"Paris": {"date": "2025-06-06", "forecast": "Sunny, 75°F"}}

# Define Agents
client_agent = Agent(
    role="Client Agent",
    goal="Understand user request and coordinate trip planning for Paris next weekend",
    backstory="A helpful assistant that interprets user needs and delegates tasks.",
    verbose=True
)

flight_agent = Agent(
    role="Flight Agent",
    goal="Find and 'book' flights to a destination for given dates",
    backstory="An expert in flight schedules and bookings.",
    verbose=True
)

hotel_agent = Agent(
    role="Hotel Agent",
    goal="Find and 'book' hotels for given dates and location",
    backstory="A specialist in hotel reservations and availability.",
    verbose=True
)

weather_agent = Agent(
    role="Weather Agent",
    goal="Provide weather forecast for a destination and date",
    backstory="A meteorology expert for travel planning.",
    verbose=True
)

# Define Tasks

client_task = Task(
    description="Interpret user request: 'Book me a trip to Paris for next weekend.' Coordinate flight, hotel, and weather info.",
    agent=client_agent,
    expected_output="A plan coordinating flight, hotel, and weather for a trip to Paris."
)
flight_task = Task(
    name="flight_task",
    description="Find a flight to Paris for next weekend (2025-06-06). Return flight number, date, time, and price.",
    agent=flight_agent,
    expected_output="Flight details: flight number, date, time, and price."
)

hotel_task = Task(
    name="hotel_task",
    description="Book a hotel in Paris for next weekend (check-in 2025-06-06, 2 nights). Return hotel name, check-in date, nights, and price.",
    agent=hotel_agent,
    expected_output="Hotel details: hotel name, check-in date, nights, and price."
)

weather_task = Task(
    name="weather_task",
    description="Get weather forecast for Paris for next weekend (2025-06-06). Return date and forecast.",
    agent=weather_agent,
    expected_output="Weather forecast: date and conditions."
)

client_crew = Crew(
    agents=[client_agent],
    tasks=[client_task],
    verbose=True
)
client_crew.kickoff()
