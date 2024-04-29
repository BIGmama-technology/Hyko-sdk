import httpx
from typing import Optional
from .models import StorageConfig


class HttpxClient:
    def __init__(
        self,
        extra_cookies: Optional[dict] = {},
        verify: Optional[bool] = False,
        timeout: Optional[int] = 10
    ):
        self.extra_cookies = extra_cookies
        self.client = httpx.AsyncClient(
            base_url=StorageConfig.host,
            timeout=timeout,
            cookies=self.merge_cookies,
            verify=verify
            )

    async def get(self, file_name) -> httpx.Response:
        url_path = f"/storage/{file_name}"
        response = await self.client.get(url=url_path)
        return response

    async def post(self, file_tuple) -> httpx.Response:
        url_path = "/storage/"
        response = await self.client.post(url=url_path, files={"file": file_tuple})
        return response

    @property
    def merge_cookies(self):
        cookies={
            "access_token": f"Bearer {StorageConfig.access_token}",
            "refresh_token": f"Bearer {StorageConfig.refresh_token}",
        },

        if self.extra_cookies:
            for key in self.extra_cookies:
                cookies[0][key] = self.extra_cookies[key]

        return cookies[0]
