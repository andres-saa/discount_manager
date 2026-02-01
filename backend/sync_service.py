"""Sincronización de sedes y menús desde el API externo."""
import asyncio
import logging
from typing import Any

import httpx

from config import MENU_API_URL_TEMPLATE, SITES_API_URL, SYNC_INTERVAL_MINUTES
from storage import read_sites_filtered, write_menu, write_sites

logger = logging.getLogger(__name__)


async def fetch_sites() -> list[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(SITES_API_URL)
        r.raise_for_status()
        return r.json()


async def fetch_menu(site_id: int) -> dict | None:
    url = MENU_API_URL_TEMPLATE.format(site_id=site_id)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        if r.status_code != 200:
            logger.warning("Menu for site %s: status %s", site_id, r.status_code)
            return None
        return r.json()


async def sync_sites():
    try:
        data = await fetch_sites()
        write_sites(data)
        logger.info("Sites synced: %s sites", len(data))
    except Exception as e:
        logger.exception("Sync sites failed: %s", e)


async def sync_menus():
    sites = read_sites_filtered()
    for site in sites:
        sid = site.get("site_id")
        if sid is None:
            continue
        try:
            menu = await fetch_menu(sid)
            if menu:
                write_menu(sid, menu)
                logger.info("Menu synced for site %s", sid)
        except Exception as e:
            logger.warning("Menu sync site %s: %s", sid, e)
        await asyncio.sleep(0.2)  # evitar saturar el API


async def run_sync_loop():
    while True:
        await sync_sites()
        await sync_menus()
        await asyncio.sleep(SYNC_INTERVAL_MINUTES * 60)
