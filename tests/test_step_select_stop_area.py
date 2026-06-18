"""Tests for the StepSelectStopArea flow logic."""

from custom_components.idf_mobilite_assistant.steps.select_stop_area import (
    StepSelectStopArea,
)
import pytest


@pytest.mark.asyncio
async def test_select_stop_area_invalid(flow_factory):
    """Ensure selecting a non-existing stop area triggers an error."""
    step = flow_factory(StepSelectStopArea)
    step._search_results = {"A": {"name": "Test", "town": "Paris", "arr_type": "bus"}}

    # Le code actuel lève KeyError → on teste ce comportement
    with pytest.raises(KeyError):
        await step.async_step_select_stop_area({"selected_stop_area": "B"})
