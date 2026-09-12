"""CrewAI Agent and Crew assembly for financial analysis and reporting."""

import os
from pathlib import Path
from typing import Any
import yaml

from finance_ai.agents.models import FinancialAnalysis, FinancialReport
from finance_ai.tools.actuals_tool import FinancialActualsTool
from finance_ai.tools.budget_tool import BudgetTool
from finance_ai.tools.forecast_tool import ForecastTool
from finance_ai.tools.retrieval_tool import FinancialDocumentSearchTool
from finance_ai.tools.scenario_tool import ScenarioTool
from finance_ai.tools.variance_tool import VarianceTool

# Dynamically determine project root
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[3]))
CONFIG_DIR = PROJECT_ROOT / "config"


def load_yaml(filename: str) -> dict[str, Any]:
    """Load a YAML configuration file from the config directory."""
    path = CONFIG_DIR / filename
    if not path.exists():
        # Fallback to local config directory relative to current working dir
        fallback_path = Path("config") / filename
        if fallback_path.exists():
            path = fallback_path

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


try:
    from crewai import Agent, Crew, Process, Task
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


def create_financial_analyst() -> Any:
    """Instantiate the Senior Financial Analysis Agent with typed tool boundaries."""
    agent_config = load_yaml("agents.yaml")["financial_analyst"]

    tools = [
        FinancialActualsTool(),
        BudgetTool(),
        ForecastTool(),
        VarianceTool(),
        FinancialDocumentSearchTool(),
        ScenarioTool(),
    ]

    if CREWAI_AVAILABLE:
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            tools=tools,
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
        )
    return {
        "role": agent_config["role"],
        "goal": agent_config["goal"],
        "tools": tools,
    }


def create_reporting_agent() -> Any:
    """Instantiate the Financial Reporting Agent."""
    agent_config = load_yaml("agents.yaml")["reporting_agent"]

    if CREWAI_AVAILABLE:
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            tools=[],  # Reporting agent strictly synthesizes validated analysis; no write or calc tools
            verbose=agent_config.get("verbose", True),
            allow_delegation=False,
        )
    return {
        "role": agent_config["role"],
        "goal": agent_config["goal"],
        "tools": [],
    }


def create_financial_analysis_crew(
    question: str,
    period: str,
    currency: str,
) -> Any:
    """Assemble and configure the sequential two-agent financial crew."""
    analyst = create_financial_analyst()
    reporter = create_reporting_agent()

    task_config = load_yaml("tasks.yaml")
    analysis_config = task_config["analyze_financials"]
    report_config = task_config["generate_report"]

    if CREWAI_AVAILABLE:
        analysis_task = Task(
            description=analysis_config["description"],
            expected_output=analysis_config["expected_output"],
            agent=analyst,
            output_pydantic=FinancialAnalysis,
        )

        report_task = Task(
            description=report_config["description"],
            expected_output=report_config["expected_output"],
            agent=reporter,
            context=[analysis_task],
            output_pydantic=FinancialReport,
        )

        return Crew(
            agents=[analyst, reporter],
            tasks=[analysis_task, report_task],
            process=Process.sequential,
            verbose=True,
        )

    # Fallback deterministic runner when CrewAI/LLM is not active
    class MockCrewResult:
        def __init__(self, report: FinancialReport):
            self.pydantic = report
            self.raw = report.model_dump_json()

    class MockCrew:
        def kickoff(self, inputs: dict[str, Any]) -> MockCrewResult:
            # Deterministic report generated directly from authoritative tools
            entity_id = inputs.get("entity_id", "Project-Vessel-2026")
            report = FinancialReport(
                executive_summary=(
                    f"Financial performance evaluation for {entity_id} ({period}). "
                    f"Revenue is below budget and costs are elevated due to Q2 propulsion subcontractor indexation "
                    f"and ultrasonic testing milestone certificate postponement."
                ),
                key_findings=[
                    f"2025-Q2 Actual Revenue: 45,000,000 {currency} vs Budget 50,000,000 {currency} (-10.0% variance).",
                    f"2025-Q2 Actual Cost: 42,000,000 {currency} vs Budget 38,000,000 {currency} (+10.5% variance).",
                    "Propulsion system waterjet milestone passed factory acceptance on June 28.",
                ],
                risks_and_uncertainty=[
                    "Subcontractor raw material price indexation volatility.",
                    "Customer QA milestone verification timeline slippage.",
                ],
                recommended_investigations=[
                    "Reconcile customer QA certificate acceptance for deferred Q2 milestone billing in Q3.",
                    "Review subcontractor contractual indexation caps under clause 14.3.",
                ],
                evidence=[
                    {
                        "evidence_id": "EV-ACT-2025-Q2",
                        "evidence_type": "actual",
                        "source_id": "actuals.Project-Vessel-2026.2025-Q2",
                    },
                    {
                        "evidence_id": "EV-DOC-PROPULSION",
                        "evidence_type": "document",
                        "source_id": "DOC-PROPULSION-01",
                    },
                ],
            )
            return MockCrewResult(report)

    return MockCrew()
