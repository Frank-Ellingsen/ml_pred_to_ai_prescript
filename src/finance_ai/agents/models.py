"""Structured Pydantic models for agent outputs with strict validation."""

from typing import Literal

from pydantic import Field

from finance_ai.domain.contracts import StrictModel


class EvidenceReference(StrictModel):
    """Reference linking an analytical finding to an authoritative source."""

    evidence_id: str
    evidence_type: Literal[
        "actual",
        "budget",
        "forecast",
        "calculation",
        "scenario",
        "document",
    ]
    source_id: str


class AnalysisFinding(StrictModel):
    """Individual financial finding grounded in evidence."""

    finding_id: str
    title: str
    metric: str
    period: str
    finding_type: Literal[
        "variance",
        "forecast_trend",
        "scenario_impact",
        "evidence_finding",
    ]
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    evidence: list[EvidenceReference] = Field(default_factory=list)


class RecommendedInvestigation(StrictModel):
    """Actionable investigation recommendation."""

    investigation_id: str
    area: str
    reason: str
    suggested_action: str
    priority: Literal["low", "medium", "high"]


class FinancialAnalysis(StrictModel):
    """Structured analytical output produced by the Financial Analyst Agent."""

    summary: str
    findings: list[AnalysisFinding] = Field(default_factory=list)
    recommendations: list[RecommendedInvestigation] = Field(default_factory=list)
    uncertainty: str
    limitations: str


class FinancialReport(StrictModel):
    """Executive financial management report produced by the Reporting Agent."""

    executive_summary: str
    key_findings: list[str] = Field(default_factory=list)
    risks_and_uncertainty: list[str] = Field(default_factory=list)
    recommended_investigations: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
