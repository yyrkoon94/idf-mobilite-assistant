"""Tests for the SearchLineStep flow logic."""

from unittest.mock import patch

from custom_components.idf_mobilite_assistant.steps.search_line import SearchLineStep
import pytest


@pytest.mark.asyncio
async def test_search_line_empty_code_all_mode(flow_factory):
    """Ensure an empty code triggers an error when mode is 'all'."""
    step = flow_factory(SearchLineStep)
    result = await step.async_step_search_line({"mode": "all", "code": ""})
    assert result["errors"]["base"] == "empty_code"


@pytest.mark.asyncio
async def test_search_line_no_results(flow_factory):
    """Ensure 'no_results' is returned when the API returns nothing."""
    step = flow_factory(SearchLineStep)

    # Simule une entry existante
    step.entry = type("obj", (), {"data": {"api_key": "FAKE"}})()

    with patch(
        "custom_components.idf_mobilite_assistant.utils.navitia_line_search.search_navitia_lines",
        return_value=[],
    ):
        result = await step.async_step_search_line({"mode": "bus", "code": "999"})
        assert result["errors"]["base"] == "no_results"
