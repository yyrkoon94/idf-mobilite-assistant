"""Tests for the SelectLineStep flow logic."""

from custom_components.idf_mobilite_assistant.steps.select_line import SelectLineStep
import pytest


@pytest.mark.asyncio
async def test_select_line_invalid_selection(flow_factory):
    """Ensure an invalid selection triggers an error."""
    step = flow_factory(SelectLineStep)
    step._line_results = [{"id": "A"}]

    result = await step.async_step_select_line({"selected_line": "B"})
    assert result["errors"]["base"] == "invalid_selection"
