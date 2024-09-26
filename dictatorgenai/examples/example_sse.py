from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import asyncio
import time


app = FastAPI()


@app.get("/events")
async def get_events(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield f"data: The server time is: {time.time()}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Interface de test HTML
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>SSE Test</title>
    </head>
    <body>
        <h1>SSE Test</h1>
        <ul id="messages">
        </ul>
        <script>
            var eventSource = new EventSource("/events");
            eventSource.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)
