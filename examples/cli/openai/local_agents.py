
from agents import Agent  
from agentkernel.openai import OpenAIModule

general_agent = Agent(
  name="general",
  instructions="You are the general agent. Start every reply with [general]."
)

summarizer_agent = Agent(
  name="summarizer",
  instructions="You summarize clearly. Start every reply with [summarizer]."
)

analyst_agent = Agent(
  name="analyst",
  instructions="You analyze local data. Start every reply with [analyst]."
)

triage_agent = Agent(
  name="triage",
  instructions=(
    "You must route the user query to the best specialist via handoff; "
    "do NOT answer yourself."
  ),
  handoffs=[analyst_agent, summarizer_agent, general_agent]
)



OpenAIModule([triage_agent, analyst_agent, summarizer_agent, general_agent])
