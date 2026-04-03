"""PEP API client — async HTTP wrapper around the Delta API."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import httpx

from primer_agent.auth import token_manager
from primer_agent.config import config

# v3 is the GA API prefix
API = "/v3"


class PEPClient:
    """Async client for the PEP (Delta) API.

    All methods handle authentication automatically via TokenManager.
    """

    def __init__(self) -> None:
        self._http: httpx.AsyncClient | None = None

    async def _client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                base_url=config.api_base_url,
                timeout=120,
            )
        return self._http

    async def _headers(self) -> dict[str, str]:
        token = await token_manager.get_token()
        return token_manager.auth_headers(token)

    async def _get(self, path: str, params: dict | None = None) -> Any:
        client = await self._client()
        resp = await client.get(path, headers=await self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, json: dict | None = None) -> Any:
        client = await self._client()
        resp = await client.post(path, headers=await self._headers(), json=json)
        resp.raise_for_status()
        return resp.json()

    async def _patch(self, path: str, json: dict | None = None) -> Any:
        client = await self._client()
        resp = await client.patch(path, headers=await self._headers(), json=json)
        resp.raise_for_status()
        return resp.json()

    async def _delete(self, path: str) -> None:
        client = await self._client()
        resp = await client.delete(path, headers=await self._headers())
        resp.raise_for_status()

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    async def search_documents(
        self,
        query: str,
        *,
        mode: str = "concept",
        start_date: str | None = None,
        end_date: str | None = None,
        sources: list[str] | None = None,
        page_size: int = 20,
    ) -> dict:
        body: dict[str, Any] = {
            "search": {
                "query": {"concept": query, "mode": mode} if mode == "concept"
                else {"terms": query, "mode": "terms"},
            },
            "results": {"page": 1, "page_size": page_size},
        }
        if start_date or end_date:
            body["search"]["published"] = {}
            if start_date:
                body["search"]["published"]["start_date"] = start_date
            if end_date:
                body["search"]["published"]["end_date"] = end_date
        if sources:
            body["search"].setdefault("metadata", {})["items"] = [
                {"key": "data_source_name", "value": s} for s in sources
            ]
        return await self._post(f"{API}/search/documents", json=body)

    async def search_aggregations(self, body: dict) -> dict:
        return await self._post(f"{API}/search/aggregations", json=body)

    # -------------------------------------------------------------------------
    # Workspaces
    # -------------------------------------------------------------------------

    async def list_workspaces(self, page: int = 1, page_size: int = 20) -> dict:
        return await self._get(
            f"{API}/workspaces",
            params={"page": page, "page_size": page_size},
        )

    async def get_workspace(self, workspace_id: str) -> dict:
        return await self._get(f"{API}/workspaces/{workspace_id}")

    async def create_workspace(
        self,
        name: str,
        *,
        dataverse_id: str | None = None,
        search_filter_ids: list[str] | None = None,
    ) -> dict:
        body: dict[str, Any] = {"name": name}
        if dataverse_id:
            body["dataverse_id"] = dataverse_id
        if search_filter_ids:
            body["search_filter_ids"] = search_filter_ids
        return await self._post(f"{API}/workspaces", json=body)

    async def delete_workspace(self, workspace_id: str) -> None:
        await self._delete(f"{API}/workspaces/{workspace_id}")

    # -------------------------------------------------------------------------
    # Dataverse (workspace document management)
    # -------------------------------------------------------------------------

    async def get_dataverse(self, dataverse_id: str) -> dict:
        return await self._get(f"{API}/dataverse/{dataverse_id}")

    async def list_dataverse_documents(
        self,
        dataverse_id: str,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        return await self._get(
            f"{API}/dataverse/{dataverse_id}/documents",
            params={"page": page, "page_size": page_size},
        )

    async def add_search_to_dataverse(
        self,
        dataverse_id: str,
        search_request: dict,
    ) -> dict:
        return await self._post(
            f"{API}/dataverse/{dataverse_id}/search",
            json={"search_request": search_request},
        )

    async def get_dataverse_aggregations(self, dataverse_id: str, version: int) -> dict:
        return await self._get(
            f"{API}/dataverse/{dataverse_id}/aggregations",
            params={"version": version},
        )

    # -------------------------------------------------------------------------
    # Conversations (AG-UI chat)
    # -------------------------------------------------------------------------

    async def send_message(
        self,
        conversation_id: str,
        message: str,
    ) -> httpx.Response:
        """Send a message to a conversation. Returns raw response for SSE streaming."""
        client = await self._client()
        headers = await self._headers()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "text/event-stream"
        return await client.post(
            f"{API}/conversations/{conversation_id}/runs",
            headers=headers,
            json={
                "thread_id": conversation_id,
                "run_id": None,
                "messages": [{"role": "user", "content": message}],
            },
            timeout=300,
        )

    async def get_conversation_messages(self, conversation_id: str) -> dict:
        return await self._get(f"{API}/conversations/{conversation_id}/messages")

    # -------------------------------------------------------------------------
    # Assets (computed insights)
    # -------------------------------------------------------------------------

    async def get_asset(self, asset_type: str, asset_id: str) -> dict:
        return await self._get(f"{API}/assets/{asset_type}/{asset_id}")

    async def get_asset_results(self, asset_type: str, asset_id: str) -> dict:
        return await self._get(f"{API}/assets/{asset_type}/{asset_id}/results")

    async def list_assets(
        self,
        dataverse_id: str,
        asset_type: str,
        *,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        return await self._get(
            f"{API}/assets/{asset_type}",
            params={
                "dataverse_id": dataverse_id,
                "page": page,
                "page_size": page_size,
            },
        )

    # -------------------------------------------------------------------------
    # Scheduled Search (AI Briefings)
    # -------------------------------------------------------------------------

    async def list_scheduled_searches(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await self._get(
            f"{API}/scheduled-search",
            params={"page": page, "page_size": page_size},
        )

    async def get_scheduled_search(self, scheduled_search_id: str) -> dict:
        return await self._get(f"{API}/scheduled-search/{scheduled_search_id}")

    async def create_scheduled_search(self, body: dict) -> dict:
        return await self._post(f"{API}/scheduled-search", json=body)

    async def get_scheduled_search_results(
        self,
        scheduled_search_id: str,
        *,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        return await self._get(
            f"{API}/scheduled-search/{scheduled_search_id}/results",
            params={"page": page, "page_size": page_size},
        )

    # -------------------------------------------------------------------------
    # Documents
    # -------------------------------------------------------------------------

    async def get_document(self, document_id: str) -> dict:
        return await self._get(f"{API}/documents/{document_id}")

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()


# Singleton
pep_client = PEPClient()
