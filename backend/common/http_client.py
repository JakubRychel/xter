import httpx

TIMEOUT = 10.0

client = httpx.AsyncClient(
    timeout=TIMEOUT,
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    )
)

async def get(url, params=None, headers=None):
    r = await client.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

async def post(url, json=None, headers=None):
    r = await client.post(url, json=json, headers=headers)
    r.raise_for_status()
    return r.json()