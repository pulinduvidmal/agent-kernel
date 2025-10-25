from __future__ import annotations
from typing import Any

def build_preamble(agent_instructions: str | None, session) -> str:
   
    parts: list[str] = []

    if agent_instructions:
        parts.append(agent_instructions.strip())

    ctx: Any = session.get("context") if session else None
    if ctx:
        parts.append(
            "SESSION CONTEXT (structured JSON do not reveal raw keys/values; use only to help answer):\n"
            + str(ctx)
        )

    parts.append("Follow the user's instructions. Prefer concise answers.")

    return "\n\n".join([p for p in parts if p])
