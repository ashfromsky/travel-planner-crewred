import httpx

from config import settings

_cache: dict[int, str] = {}


class AICService:
    def __init__(self):
        self.base_url = settings.AIC_BASE_URL

    async def get_artwork(self, external_id: str | int) -> dict | None:
        try:
            ext_id = int(external_id)
        except (ValueError, TypeError):
            return None

        if ext_id in _cache:
            return {"id": ext_id, "title": _cache[ext_id]}

        url = f"{self.base_url}/artworks/{ext_id}?fields=id,title"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers={"AIC-User-Agent": "travel-planner (test-assessment)"},
                )
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        data = response.json().get("data", {})
        title = data.get("title", f"Artwork #{ext_id}")

        _cache[ext_id] = title
        return {"id": ext_id, "title": title}


aic_service = AICService()