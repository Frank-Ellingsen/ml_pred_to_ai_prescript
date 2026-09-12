"""BaseTool abstraction compatible with CrewAI with lightweight fallback."""

from typing import Any

try:
    from crewai.tools import BaseTool
except (ImportError, TypeError):
    from pydantic import BaseModel

    class BaseTool(BaseModel):  # type: ignore[no-redef]
        name: str = ""
        description: str = ""
        args_schema: type[BaseModel] | None = None

        def run(self, *args: Any, **kwargs: Any) -> Any:
            return self._run(*args, **kwargs)

        def _run(self, *args: Any, **kwargs: Any) -> Any:
            raise NotImplementedError
