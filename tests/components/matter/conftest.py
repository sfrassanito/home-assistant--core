"""Provide common fixtures."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from matter_server.client.client import Client
from matter_server.client.model.device_controller import DeviceController
from matter_server.client.model.driver import Driver
from matter_server.client.model.read_subscriptions import ReadSubscriptions
from matter_server.common.model.message import ServerInformation
import pytest

from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


@pytest.fixture(name="matter_client")
async def matter_client_fixture() -> AsyncGenerator[MagicMock, None]:
    """Fixture for a Matter client."""
    with patch("homeassistant.components.matter.Matter", autospec=True) as client_class:
        client = client_class.return_value
        client.client = MagicMock(spec=Client)
        client.driver_ready = asyncio.Event()

        async def connect() -> None:
            """Mock connect."""
            adapter = client_class.call_args[0][0]
            client.adapter = adapter
            client.client.server_info = MagicMock(spec=ServerInformation)
            await asyncio.sleep(0)
            client.connected = True

        def listen() -> None:
            """Mock listen."""
            client.client.driver = MagicMock(spec=Driver)
            client.client.driver.device_controller = MagicMock(spec=DeviceController)
            client.client.driver.read_subscriptions = ReadSubscriptions(client)
            client.client.driver.server_info = MagicMock(client.client.server_info)
            client.driver_ready.set()

        client.connect = AsyncMock(side_effect=connect)
        client.listen = MagicMock(side_effect=listen)

        yield client


@pytest.fixture(name="integration")
async def integration_fixture(
    hass: HomeAssistant, matter_client: MagicMock
) -> MockConfigEntry:
    """Set up the Matter integration."""
    entry = MockConfigEntry(
        domain="matter", data={"url": "ws://localhost:5580/chip_ws"}
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


@pytest.fixture(name="create_backup")
def create_backup_fixture() -> Generator[AsyncMock, None, None]:
    """Mock Supervisor create backup of add-on."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_create_backup"
    ) as create_backup:
        yield create_backup


@pytest.fixture(name="addon_store_info")
def addon_store_info_fixture() -> Generator[AsyncMock, None, None]:
    """Mock Supervisor add-on store info."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_get_addon_store_info"
    ) as addon_store_info:
        addon_store_info.return_value = {
            "installed": None,
            "state": None,
            "version": "1.0.0",
        }
        yield addon_store_info


@pytest.fixture(name="addon_info")
def addon_info_fixture() -> Generator[AsyncMock, None, None]:
    """Mock Supervisor add-on info."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_get_addon_info",
    ) as addon_info:
        addon_info.return_value = {
            "hostname": None,
            "options": {},
            "state": None,
            "update_available": False,
            "version": None,
        }
        yield addon_info


@pytest.fixture(name="addon_not_installed")
def addon_not_installed_fixture(
    addon_store_info: AsyncMock, addon_info: AsyncMock
) -> AsyncMock:
    """Mock add-on not installed."""
    return addon_info


@pytest.fixture(name="addon_installed")
def addon_installed_fixture(
    addon_store_info: AsyncMock, addon_info: AsyncMock
) -> AsyncMock:
    """Mock add-on already installed but not running."""
    addon_store_info.return_value = {
        "installed": "1.0.0",
        "state": "stopped",
        "version": "1.0.0",
    }
    addon_info.return_value["hostname"] = "core-matter-server"
    addon_info.return_value["state"] = "stopped"
    addon_info.return_value["version"] = "1.0.0"
    return addon_info


@pytest.fixture(name="addon_running")
def addon_running_fixture(
    addon_store_info: AsyncMock, addon_info: AsyncMock
) -> AsyncMock:
    """Mock add-on already running."""
    addon_store_info.return_value = {
        "installed": "1.0.0",
        "state": "started",
        "version": "1.0.0",
    }
    addon_info.return_value["hostname"] = "core-matter-server"
    addon_info.return_value["state"] = "started"
    addon_info.return_value["version"] = "1.0.0"
    return addon_info


@pytest.fixture(name="install_addon")
def install_addon_fixture(
    addon_store_info: AsyncMock, addon_info: AsyncMock
) -> Generator[AsyncMock, None, None]:
    """Mock install add-on."""

    async def install_addon_side_effect(hass: HomeAssistant, slug: str) -> None:
        """Mock install add-on."""
        addon_store_info.return_value = {
            "installed": "1.0.0",
            "state": "stopped",
            "version": "1.0.0",
        }
        addon_info.return_value["state"] = "stopped"
        addon_info.return_value["version"] = "1.0.0"

    with patch(
        "homeassistant.components.hassio.addon_manager.async_install_addon"
    ) as install_addon:
        install_addon.side_effect = install_addon_side_effect
        yield install_addon


@pytest.fixture(name="start_addon")
def start_addon_fixture() -> Generator[AsyncMock, None, None]:
    """Mock start add-on."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_start_addon"
    ) as start_addon:
        yield start_addon


@pytest.fixture(name="stop_addon")
def stop_addon_fixture() -> Generator[AsyncMock, None, None]:
    """Mock stop add-on."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_stop_addon"
    ) as stop_addon:
        yield stop_addon


@pytest.fixture(name="uninstall_addon")
def uninstall_addon_fixture() -> Generator[AsyncMock, None, None]:
    """Mock uninstall add-on."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_uninstall_addon"
    ) as uninstall_addon:
        yield uninstall_addon


@pytest.fixture(name="update_addon")
def update_addon_fixture() -> Generator[AsyncMock, None, None]:
    """Mock update add-on."""
    with patch(
        "homeassistant.components.hassio.addon_manager.async_update_addon"
    ) as update_addon:
        yield update_addon
