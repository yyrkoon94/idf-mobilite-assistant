"""Tests for the SearchStopAreaStep flow logic."""

from custom_components.idf_mobilite_assistant.steps.search_stop_area import (
    SearchStopAreaStep,
)
import pytest


@pytest.mark.asyncio
async def test_search_stop_area_too_short(flow_factory):
    """Ensure a too-short query triggers an error."""
    step = flow_factory(SearchStopAreaStep)
    result = await step.async_step_search_stop_area({"search": "Ga"})
    assert result["errors"]["base"] == "query_too_short"
