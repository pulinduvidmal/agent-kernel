import logging
import uuid
from typing import Optional, Dict, Any   

from ..core import Runtime, Agent, Session


class AgentService:
    """
    AgentService class provides a utility method for interacting with runtime, agents and sessions.
    The agent service encapsulates a conversation of a single session with a single agent.
    """

    def __init__(self):
        self._log = logging.getLogger("ak.core.service.agentservice")
        self._agent: Optional[Agent] = None
        self._session: Optional[Session] = None
        self._runtime = Runtime.instance()

    @property
    def runtime(self) -> Runtime:
        return self._runtime

    @property
    def agent(self) -> Optional[Agent]:
        return self._agent

    @property
    def session(self) -> Optional[Session]:
        return self._session

    def reset(self):
        self._agent = None
        self._session = None

    def select(self, session_id: str | None = None, name: str | None = None):
        if name:
            selected = self._runtime.agents().get(name)
            if selected:
                self._agent = selected
            else:
                self._log.warning(f"No agent found with name '{name}'")
        else:
            self._log.info("No agent was requested. Defaulting to first agent in the list")
            agents = list(self._runtime.agents().values())
            self._agent = agents[0] if agents else None
            if self._agent:
                self._log.info(f"Selected agent: {self._agent.name}")
            else:
                self._log.error("No agents available")

        if self._agent:
            if session_id is not None:
                self._old(session_id)
            else:
                self.new()
        else:
            self._log.warning("No agent selected. Session was not created.")

    def _old(self, session_id: str):
        self._log.debug(f"Attempting to reuse existing session: {session_id}")
        self._session = self._runtime.sessions().load(session_id)

    def new(self):
        session_id = str(uuid.uuid4())
        self._log.info(f"Starting new session: {session_id}")
        self._session = self._runtime.sessions().new(session_id)

    def load(self, session_id: str, name: str):
        try:
            self._runtime.load(name)
            if not self._agent:
                self.select(session_id)
        except ImportError as e:
            self._log.info(f"No module found with name '{name}': {e}")
            return None

    async def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
       
        if context is not None and self._session:
            self._session.set("context", context)

        result = await self._runtime.run(self._agent, self._session, prompt)

       
        self._runtime.sessions().store(self._session)
        return result

    def get_response_session_id(self, session_id: str | None = None) -> str | None:
        return self._session.id if self._session else session_id
