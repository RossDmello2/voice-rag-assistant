import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AsyncHttpClient:
    """
    Singleton HTTP client to provide connection pooling and reduce handshake latency.
    """
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            logger.info("Initializing shared Singleton HTTP Client pool")
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info("Shared HTTP Client pool closed")

# Global access helper
async def get_http_client() -> httpx.AsyncClient:
    return await AsyncHttpClient.get_client()
