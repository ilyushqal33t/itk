import json
import httpx
from typing import Dict, Any, Callable
import uvicorn


async def app(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    if scope["type"] != "http":
        return

    path = scope["path"].strip("/")
    if not path or len(path) > 3:
        await send_error(send, 400, "Invalid currency code")
        return

    currency = path.upper()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.exchangerate-api.com/v4/latest/{currency}", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                await send_response(send, 200, data)
            else:
                await send_error(send, response.status_code, "Api error")

    except httpx.TimeoutException:
        await send_error(send, 504, "External Api timeout")
    except httpx.RequestError:
        await send_error(send, 502, "External Api unavailable")
    except Exception as e:
        await send_error(send, 500, f"Internal server error: {str(e)}")


async def send_response(send: Callable, status: int, data: Dict[str, Any]) -> None:
    body = json.dumps(data).encode("utf-8")

    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"access-control-allow-origin", b"*"],
            ],
        }
    )

    await send({"type": "http.response.body", "body": body})


async def send_error(send: Callable, status: int, message: str) -> None:
    error_data = {"error": True, "status": status, "message": message}

    body = json.dumps(error_data).encode("utf-8")

    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
            ],
        }
    )

    await send({"type": "http.response.body", "body": body})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
