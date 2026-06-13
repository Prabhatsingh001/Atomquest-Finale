import asyncio
import livekit.api

async def main():
    api_client = livekit.api.LiveKitAPI('http://1', 'k', 's')
    print(dir(api_client.egress))
    await api_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
