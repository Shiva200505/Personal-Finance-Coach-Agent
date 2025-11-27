import os
from typing import Optional, Dict

from utils.memory import Memory
from utils.logger import get_logger
from tools.storage_tool import StorageTool
from tools.search_tool import SearchTool
from agents.expense_tracker_agent import ExpenseTrackerAgent
from agents.budget_analyzer_agent import BudgetAnalyzerAgent
from agents.savings_advisor_agent import SavingsAdvisorAgent
from agents.goal_monitor_agent import GoalMonitorAgent

try:
    import google.generativeai as genai
except Exception:
    genai = None


class CoordinatorAgent:
    """
    Main orchestrator agent:
    - Initializes sub-agents and shared tools
    - Uses Gemini (if configured) to understand user intent
    - Maintains conversation context and preferences
    - Routes tasks to appropriate sub-agent
    """

    def __init__(self, session_id: str = "default") -> None:
        self.logger = get_logger("coordinator")
        self.memory = Memory(session_id=session_id)
        self.storage = StorageTool()
        self.search = SearchTool()

        # Configure Gemini model
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                # Use a lightweight model by default, can switch to gemini-pro
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.logger.info("Gemini model initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None

        # Sub-agents
        self.expense_agent = ExpenseTrackerAgent(self.storage)
        self.budget_agent = BudgetAnalyzerAgent(self.storage, self.model)
        self.savings_agent = SavingsAdvisorAgent(self.storage, self.search)
        self.goal_agent = GoalMonitorAgent(self.storage)

    def classify_intent(self, text: str) -> str:
        """Classify user intent into one of: expense, budget, advice, goal, report, help."""
        lower = text.lower().strip()
        # Quick rule-based fallback
        if any(k in lower for k in ["spent", "buy", "paid", "expense"]):
            return "expense"
        if any(k in lower for k in ["budget", "analysis", "overspend"]):
            return "budget"
        if any(k in lower for k in ["save money", "advice", "tips"]):
            return "advice"
        if any(k in lower for k in ["goal", "save", "target"]):
            return "goal"
        if any(k in lower for k in ["report", "summary"]):
            return "report"
        if "help" in lower:
            return "help"

        # Gemini-based classification for free-form text
        if self.model:
            prompt = (
                "Classify the user's intent into one of: expense, budget, advice, goal, report, help. "
                "Return only the label.\nUser: " + text
            )
            try:
                resp = self.model.generate_content(prompt)
                label = resp.text.strip().lower()
                if label in {"expense", "budget", "advice", "goal", "report", "help"}:
                    return label
            except Exception as e:
                self.logger.warning(f"Gemini classify failed: {e}")
        return "help"

    def handle(self, text: str, explicit_command: Optional[str] = None) -> Dict[str, str]:
        """Route the input to the appropriate sub-agent and return response."""
        self.logger.info(f"User input: {text}")
        self.memory.append_conversation("user", text)

        intent = explicit_command or self.classify_intent(text)
        self.logger.info(f"Detected intent: {intent}")

        try:
            if intent == "expense":
                result = self.expense_agent.add_expense(text)
                msg = result["message"]
            elif intent == "budget":
                result = self.budget_agent.analyze_current_month()
                msg = result["analysis"]
            elif intent == "advice":
                result = self.savings_agent.advise()
                msg = self._format_advice(result)
            elif intent == "goal":
                msg = "Use /goal to set, list, or view progress."
            elif intent == "report":
                msg = self._generate_report()
            else:
                msg = self._help_text()
        except Exception as e:
            self.logger.error(f"Agent handling error: {e}")
            msg = f"Error: {e}"

        self.memory.append_conversation("agent", msg)
        return {"response": msg}

    def _format_advice(self, data: Dict[str, any]) -> str:
        lines = ["Personalized Savings Advice:"]
        lines.append("Spending (last 30 days):")
        for k, v in data["pattern_summary"].items():
            lines.append(f"- {k}: ${v:.2f}")
        lines.append("Suggestions:")
        for t in data["personalized_tips"]:
            lines.append(f"- {t}")
        if data["web_tips"]:
            lines.append("Web tips:")
            for w in data["web_tips"]:
                lines.append(f"- {w}")
        return "\n".join(lines)

    def _generate_report(self) -> str:
        now = __import__("datetime").datetime.now()
        totals = self.storage.totals_by_category(now.year, now.month)
        lines = ["Monthly Spending Report:"]
        for k, v in totals.items():
            lines.append(f"- {k}: ${v:.2f}")
        lines.append(f"Total: ${sum(totals.values()):.2f}")
        return "\n".join(lines)

    def _help_text(self) -> str:
        return (
            "Available commands:\n"
            "/help  - show all commands\n"
            "/expense  - add an expense (e.g., 'I spent $50 on groceries')\n"
            "/budget  - view budget analysis\n"
            "/advice  - get savings advice\n"
            "/goal  - set or view goals\n"
            "/report  - generate spending report\n"
            "/quit  - exit\n"
        )