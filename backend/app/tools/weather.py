import httpx


async def get_weather(location: str) -> str:
    """Fetch current weather from wttr.in (free, no API key)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://wttr.in/{location}",
                params={"format": "3"},
                headers={"User-Agent": "NexusAI/1.0"},
            )
            if resp.status_code == 200:
                return f"🌤️ {resp.text.strip()}"
            return f"Could not fetch weather for **{location}** (HTTP {resp.status_code})."
    except httpx.TimeoutException:
        return f"Weather service timed out for **{location}**. Please try again."
    except Exception as exc:
        return f"Weather service error: {exc}"
