"""Tests for the StepUser initial flow logic."""

from custom_components.idf_mobilite_assistant.steps.user import StepUser
import pytest


@pytest.mark.asyncio
async def test_step_user_redirect_if_existing(flow_factory):
    """Ensure the user is redirected to the main menu if a config already exists."""
    step = flow_factory(StepUser)
    step._async_current_entries = lambda: [type("obj", (), {})()]

    result = await step.async_step_user()
    assert result["step_id"] == "main_menu"
