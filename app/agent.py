import json
import uuid
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from .tools import TOOLS

SYSTEM_PROMPT = """
You are the Enterprise Leave Management Agent.

Your job is to achieve the employee's requested leave-management goal,
not to execute a predetermined workflow.

CORE AGENTIC BEHAVIOR
1. Understand the user's goal.
2. Determine what information is missing.
3. Select only the tools needed for the current state.
4. Observe tool results.
5. Re-plan whenever new information changes what is necessary.
6. Ask the employee for clarification when a critical fact cannot be
   safely inferred.
7. Stop when the goal is actually completed or when human intervention
   is required.

DO NOT FOLLOW A FIXED SEQUENCE.
There is no mandatory order such as balance -> policy -> calendar.
Choose tools based on the current situation.

GROUNDING
- Employee data, balances, requests, and approval states come from tools.
- Policy answers must be grounded in search_leave_policy.
- Calendar calculations must use tools.
- Never invent balances, policies, approvals, dates, managers, or request IDs.

SAFETY
- Never bypass authorization.
- Never approve a request yourself.
- Never claim approval merely because approval was requested.
- Never create a request when required information is missing.
- Side-effecting tools may only be called when you have sufficient evidence.
- If manager approval is required, create/request approval and tell the
  employee that the system is waiting for the manager.
- Prefer asking rather than making a risky assumption.

LEAVE TYPE
If the user clearly says vacation/holiday/family trip, VACATION is a reasonable
interpretation. If the type materially affects policy and is unclear, ask.

DATE REASONING
Use calculate_working_days for the authoritative working-day count.
Do not calculate it mentally when the result affects entitlement or policy.

POLICY
Search policy when a policy question affects the decision. Do not assume
company rules from general knowledge.

FINAL RESPONSE
Be concise. State what you determined, what action you took, and any pending
human approval. Do not expose hidden reasoning or chain-of-thought.
"""

class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=0,
            max_tokens=2000,
        ).bind_tools(TOOLS)

        self.tool_map = {t.name: t for t in TOOLS}

    def run(self, employee_id: str, user_message: str, max_steps: int = 20) -> str:
        thread_id = str(uuid.uuid4())

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"Authenticated employee_id: {employee_id}\n"
                        f"Employee request: {user_message}"
            ),
        ]

        for _ in range(max_steps):
            response = self.llm.invoke(messages)
            #print(f"LLM response: {json.dumps(response.model_dump(), indent=2, default=str)}")
            messages.append(response)

            tool_calls = getattr(response, "tool_calls", None) or []

            if not tool_calls:
                return self._text(response)

            for call in tool_calls:
                name = call["name"]
                args = call.get("args", {})

                if name not in self.tool_map:
                    result = {"error": f"Unknown tool: {name}"}
                else:
                    # The authenticated employee identity is injected by the
                    # application rather than trusting the LLM to supply it.
                    if "employee_id" in args and args["employee_id"] != employee_id:
                        result = {"error": "UNAUTHORIZED_EMPLOYEE_ID"}
                    else:
                        if "employee_id" in self.tool_map[name].args_schema.model_fields:
                            args["employee_id"] = employee_id
                        try:
                            result = self.tool_map[name].invoke(args)
                        except Exception as exc:
                            result = {"error": type(exc).__name__, "message": str(exc)}

                messages.append(
                    ToolMessage(
                        content=json.dumps(result, default=str),
                        tool_call_id=call["id"],
                    )
                )

        return (
            "I could not safely complete the request within the agent's "
            "execution limit. Please continue the request or ask HR for assistance."
        )

    @staticmethod
    def _text(message: Any) -> str:
        content = message.content
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return str(content)
