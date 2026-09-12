"""CrewAI Flow managing deterministic state lifecycle for financial analysis."""

from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import Field

from finance_ai.agents.crew import create_financial_analysis_crew
from finance_ai.agents.models import FinancialReport
from finance_ai.domain.contracts import StrictModel

T = TypeVar("T")

try:
    from crewai.flow.flow import Flow, listen, start
except (ImportError, TypeError):
    # Lightweight fallback when crewai flow dependencies are absent
    def start():
        def decorator(fn):
            fn.__is_start__ = True
            return fn
        return decorator

    def listen(target):
        def decorator(fn):
            fn.__target__ = target
            return fn
        return decorator

    class Flow(Generic[T]):
        def __init__(self):
            # Inspect annotations for state type
            state_cls = getattr(self, "__orig_bases__", [None])[0]
            if state_cls and hasattr(state_cls, "__args__"):
                self.state = state_cls.__args__[0]()
            else:
                self.state = FinancialAnalysisFlowState()

        def kickoff(self) -> Any:
            # Sequential execution of start -> listen methods
            ctx = self.prepare_analysis()
            result = self.run_analysis(ctx)
            return self.finalize(result)


class FinancialAnalysisFlowState(StrictModel):
    """Structured, typed state owned by the Flow."""

    analysis_id: UUID = Field(default_factory=uuid4)
    question: str = ""
    entity_id: str = "Project-Vessel-2026"
    period: str = ""
    currency: str = "NOK"
    report: FinancialReport | None = None
    status: str = "created"


class FinancialAnalysisFlow(Flow[FinancialAnalysisFlowState]):
    """Flow-first execution controller for the Predict-to-Prescribe lifecycle."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not hasattr(self, "state") or self.state is None:
            self.state = FinancialAnalysisFlowState()

    @start()
    def prepare_analysis(self) -> dict[str, Any]:
        """Validate state and initialize workflow context."""
        self.state.status = "analysis_started"
        return {
            "analysis_id": str(self.state.analysis_id),
            "question": self.state.question,
            "entity_id": self.state.entity_id,
            "period": self.state.period,
            "currency": self.state.currency,
        }

    @listen(prepare_analysis)
    def run_analysis(self, context: dict[str, Any]) -> Any:
        """Invoke the bounded Crew with strictly typed inputs."""
        crew = create_financial_analysis_crew(
            question=context["question"],
            period=context["period"],
            currency=context["currency"],
        )

        result = crew.kickoff(
            inputs={
                "question": context["question"],
                "period": context["period"],
                "currency": context["currency"],
                "entity_id": context["entity_id"],
            }
        )

        self.state.status = "analysis_completed"
        return result

    @listen(run_analysis)
    def finalize(self, result: Any) -> FinancialAnalysisFlowState:
        """Validate and attach the structured report to the final flow state."""
        if hasattr(result, "pydantic") and result.pydantic:
            if isinstance(result.pydantic, FinancialReport):
                self.state.report = result.pydantic
            else:
                self.state.report = FinancialReport.model_validate(result.pydantic)
        elif isinstance(result, dict) and "report" in result:
            self.state.report = FinancialReport.model_validate(result["report"])

        self.state.status = "completed"
        return self.state
