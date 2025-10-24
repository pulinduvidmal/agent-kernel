
from agents import Agent  
from agentkernel.openai import OpenAIModule


general_agent = Agent(
    name="general",
    handoff_description="General-purpose Q&A and explanations.",
    instructions=(
        "You answer general user questions. Be concise and accurate. "
        "If the user asks about local news or facts that may be in our local files, "
        "say you will consult the analyst or wait for provided notes."
    ),
)

summarizer_agent = Agent(
    name="summarizer",
    handoff_description="Turns analyst notes into a final answer with citations.",
    instructions=(
        "You receive NOTES gathered from local files and produce a final answer.\n"
        "Rules:\n"
        "- Only use information found in NOTES; do not invent facts.\n"
        "- Write 3–6 sentences unless the user asked for a specific format.\n"
        "- Cite sources as [1], [2], etc. (matching the bracketed indices in NOTES).\n"
        "- If NOTES are empty, say you could not find local information."
    ),
)

analyst_agent = Agent(
    name="analyst",
    handoff_description="Finds evidence/snippets from local newspaper files (RAG) and returns NOTES.",
    instructions=(
        "Your job is to gather short evidence snippets from local files relevant to the user question. "
        "Return ONLY a notes section in this format:\n"
        "NOTES:\n"
        "[1] <short snippet 1> (source: <filename>)\n"
        "[2] <short snippet 2> (source: <filename>)\n"
        "...\n"
        "If nothing relevant is found, return:\n"
        "NOTES:\n- No local matches.\n"
        "Do not write a final answer—that is the summarizer's job."
    ),
)

triage_agent = Agent(
    name="triage",
    instructions=(
        "Route the user query to the most suitable agent:\n"
        "- If it's about local news, local events, Colombo/Moratuwa updates, or facts likely in local newspapers: use the ANALYST.\n"
        "- If it's purely math/calculation: use the MATH agent.\n"
        "- Otherwise: use the GENERAL agent.\n"
        "Keep answers short. If you directly answer, be concise."
    ),

    handoffs=[analyst_agent, summarizer_agent, general_agent],
)


OpenAIModule([triage_agent, analyst_agent, summarizer_agent, general_agent])
