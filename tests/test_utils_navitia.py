"""Tests for the Navitia line search utility."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from custom_components.idf_mobilite_assistant.utils.navitia_line_search import (
    search_navitia_lines,
)
import pytest


@pytest.mark.asyncio
async def test_search_navitia_lines_returns_results():
    """Ensure the function returns parsed lines when the API responds normally."""
    fake_json = {
        "pt_objects": [
            {
                "line": {
                    "id": "line:IDFM:123",
                    "name": "Ligne 123",
                    "code": "123",
                    "commercial_mode": {"name": "Bus"},
                }
            }
        ]
    }

    with patch("aiohttp.ClientSession") as mock_session_cls:
        # Fake response object
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=fake_json)
        mock_resp.__aenter__.return_value = mock_resp
        mock_resp.__aexit__.return_value = False

        # Fake session object
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_resp
        mock_session.get.return_value.__aexit__.return_value = False

        # aiohttp.ClientSession() → mock_session
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_navitia_lines("APIKEY", "bus", "123")

        assert len(results) == 1
        assert results[0]["id"] == "line:IDFM:123"


@pytest.mark.asyncio
async def test_navitia_http_error_returns_empty():
    """If Navitia returns a non-200 status, the function must return an empty list."""
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

        results = await search_navitia_lines("APIKEY", "bus", "123")
        assert results == []


@pytest.mark.asyncio
async def test_navitia_timeout_returns_empty():
    """If a timeout occurs, the function must return an empty list."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_sess = MagicMock()
        mock_sess.get.side_effect = TimeoutError()

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_navitia_lines("APIKEY", "bus", "123")
        assert results == []


@pytest.mark.asyncio
async def test_navitia_invalid_json_returns_empty():
    """If JSON decoding fails, the function must return an empty list."""
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

        results = await search_navitia_lines("APIKEY", "bus", "123")
        assert results == []


@pytest.mark.asyncio
async def test_navitia_client_error_returns_empty():
    """If aiohttp raises a ClientError, the function must return an empty list."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_sess = MagicMock()
        mock_sess.get.side_effect = aiohttp.ClientError("Network error")

        mock_session_cls.return_value.__aenter__.return_value = mock_sess
        mock_session_cls.return_value.__aexit__.return_value = False

        results = await search_navitia_lines("APIKEY", "bus", "123")
        assert results == []
