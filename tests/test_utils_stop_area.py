"""Tests for the local stop area search utility."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from custom_components.idf_mobilite_assistant.utils.prim_stop_area_search import (
    search_local_stop_areas,
)
import pytest


@pytest.mark.asyncio
async def test_search_local_stop_areas_returns_results():
    """Ensure stop areas are parsed correctly from the API response."""
    fake_json = {
        "records": [
            {
                "fields": {
                    "zdaid": "123",
                    "zdcid": None,
                    "zdaname": "Gare de Lyon",
                    "zdatown": "Paris",
                    "zdatype": "metroStation",
                }
            }
        ]
    }

    with patch("aiohttp.ClientSession") as mock_session_cls:
        # Fake response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=fake_json)
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__.return_value = False

        # Fake session
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_resp
        mock_session.get.return_value.__aexit__.return_value = False

        mock_session_cls.return_value.__aenter__.return_value = mock_session
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_local_stop_areas("Gare")

        assert "STIF:StopArea:SP:123:" in results
        entry = results["STIF:StopArea:SP:123:"]
        assert entry["name"] == "Gare de Lyon"
        assert entry["town"] == "Paris"
        assert entry["arr_type"] == "metro"


@pytest.mark.asyncio
async def test_stop_area_http_error_returns_empty():
    """If API returns non-200, the function must return an empty dict."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.json = AsyncMock(return_value={})
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__.return_value = False

        mock_sess = MagicMock()
        mock_sess.get.return_value.__aenter__.return_value = mock_resp
        mock_sess.get.return_value.__aexit__.return_value = False

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_local_stop_areas("Gare")
        assert results == {}


@pytest.mark.asyncio
async def test_stop_area_timeout_returns_empty():
    """If a timeout occurs, the function must return an empty dict."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_sess = MagicMock()
        mock_sess.get.side_effect = TimeoutError()

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_local_stop_areas("Gare")
        assert results == {}


@pytest.mark.asyncio
async def test_stop_area_invalid_json_returns_empty():
    """If JSON decoding fails, the function must return an empty dict."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__.return_value = False

        mock_sess = MagicMock()
        mock_sess.get.return_value.__aenter__.return_value = mock_resp
        mock_sess.get.return_value.__aexit__.return_value = False

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_local_stop_areas("Gare")
        assert results == {}


@pytest.mark.asyncio
async def test_stop_area_client_error_returns_empty():
    """If aiohttp raises a ClientError, the function must return an empty dict."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_sess = MagicMock()
        mock_sess.get.side_effect = aiohttp.ClientError("Network error")

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_local_stop_areas("Gare")
        assert results == {}
