"""Tests for the StepUpdateApi flow logic."""

from custom_components.idf_mobilite_assistant.steps.update_api import StepUpdateApi
import pytest


@pytest.mark.asyncio
async def test_update_api_empty(flow_factory):
    """Ensure an empty API key triggers an error."""
    step = flow_factory(StepUpdateApi)
    step.entry = type("obj", (), {"data": {"api_key": ""}})()

    result = await step.async_step_update_api_key({"api_key": ""})
    assert result["errors"]["base"] == "api_key_empty"
