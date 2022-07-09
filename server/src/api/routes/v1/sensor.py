from asyncio import sleep
from datetime import datetime, timedelta, timezone
from typing import List
from async_timeout import timeout
from fastapi import APIRouter, Depends, Request, Response
from sse_starlette import EventSourceResponse

from src.api.contexts.stream import StreamContext
from src.api.contexts.data import DataContext
from src.models.sensor import SensorReading

router = APIRouter(prefix="/v1/sensor", tags=["v1", "sensor"])


@router.get(
    "/stream",
    name="Stream Sensor",
    response_class=Response(media_type="text/event-stream"),
)
async def stream(
    request: Request,
    stream: StreamContext = Depends(StreamContext.depends),
):
    """
    Stream sensor data from the API via [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events), published at 2 second intervals.

    The data is JSON formatted with the following structure:
    ```
    {
        "timestamp": date-time,
        "channel": string,
        "data": {
            "temperature": float,
            "humidity": integer
        }
    }
    ```
    Note on units:
    - `timestamp` is UTC
    - `temperature` is celcius (C)
    - `humidity` is percent relative humidity (%RH)
    """

    return EventSourceResponse(stream.subscribe(request.is_disconnected))


@router.get("/history", name="Read Sensor History", response_model=List[SensorReading])
async def history(
    start: datetime = datetime.now(timezone.utc) - timedelta(days=1),
    end: datetime = datetime.now(timezone.utc),
    data: DataContext = Depends(DataContext.depends),
):
    history = await data.sensor.get_history(start, end)
    return history