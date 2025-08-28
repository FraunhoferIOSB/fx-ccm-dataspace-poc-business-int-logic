from fastapi import APIRouter, Request
from app.datamodels import MachineReading
from datetime import datetime, timedelta
from typing import Dict

# helpers:
from app.routes.utils import generate_random_machine_readings

# create router:
router = APIRouter(prefix='/gen', tags=['generator', 'gen'])

# helpers:
time_format: str = "%Y-%m-%d %H:%M:%S"


def exceeded_timeframe(s1: str, s2: str) -> bool:
    """
    Takes two strings with a given time format and checks
    whether both are more than a number of predefined
    seconds apart.
    """
    t1 = datetime.strptime(s1, time_format)
    t2 = datetime.strptime(s2, time_format)
    return abs(t1 - t2) > timedelta(milliseconds=700)


def gen_machine_reading(readable_timestamp: str) -> MachineReading:
    """
    Generates new, random Machine reading.

    Args:
    - readable_timestamp: timestamp of the format "%Y-%m-%d %H:%M:%S"

    Returns:
    - MachineReading
    """
    temperature, current, speed = generate_random_machine_readings()

    return MachineReading(
        timestamp=readable_timestamp,
        temperature=temperature,
        current=current,
        speed=speed
    )


# --- Current Machine Readings ---
@router.get("/machinereadings", status_code=200, response_model=MachineReading)
async def get_machinereadings(request: Request):
    """
    Generates Dummy Machine Readings at the current time stamp.
    Readings are freshly generated if the last machine reading is older
    than 1 second.

    Args: -
    Returns: JSON with a human readable time stamp and
        dummy machine readings (up to 3rd decimal precision).
    """
    # get the current timestamp that binds values together
    current_time: datetime = datetime.now()
    readable_timestamp: str = current_time.strftime(time_format)

    # check the latest generated timestamp
    async with request.app.state.lock:
        machine_reading = request.app.state.generated_machine_reading

    # return current machine reading?
    if machine_reading is not None and \
        not exceeded_timeframe(
            readable_timestamp, machine_reading.timestamp):
        return machine_reading

    new_machine_reading = gen_machine_reading(readable_timestamp)

    # store for other request within 1 second:
    async with request.app.state.lock:
        request.app.state.generated_machine_reading = new_machine_reading

    return new_machine_reading


@router.get("/units")
def get_machinereading_units() -> Dict[str, str]:
    """
    Lookup for the units of the Dummy Machine Readings.
    Args: -
    Returns: JSON with units of the machine readings
    """
    # hardcoded units
    machine_reading_units: Dict[str, str] = {
        "temperature": 'Celcius',
        "current": 'A',
        "speed": 'rpm',
    }
    return machine_reading_units


# = dedicated paths =
@router.get("/Temperature", status_code=200)
async def get_temperature(request: Request) -> Dict[str, str | float]:
    """
    Get Temperature from the Maschine Reading.
    New Machine Reading is generated if a predefined timeframe passed
    (currently 1 second).
    """
    # get the current timestamp that binds values together
    current_time: datetime = datetime.now()
    readable_timestamp: str = current_time.strftime(time_format)

    # check the latest generated timestamp
    async with request.app.state.lock:
        machine_reading = request.app.state.generated_machine_reading

    # return current machine reading?
    if machine_reading is not None and \
        not exceeded_timeframe(
            readable_timestamp, machine_reading.timestamp):
        return {"Value": machine_reading.temperature,
                "Timestamp": machine_reading.timestamp}

    new_machine_reading = gen_machine_reading(readable_timestamp)

    # store for other request within 1 second:
    async with request.app.state.lock:
        request.app.state.generated_machine_reading = new_machine_reading

    return {"Value": new_machine_reading.temperature,
            "Timestamp": new_machine_reading.timestamp}


@router.get("/Current", status_code=200)
async def get_current(request: Request) -> Dict[str, str | float]:
    """
    Get current Current from the Maschine Reading.
    New Machine Reading is generated if a predefined timeframe passed
    (currently 1 second).
    """
    # get the current timestamp that binds values together
    current_time: datetime = datetime.now()
    readable_timestamp: str = current_time.strftime(time_format)

    # check the latest generated timestamp
    async with request.app.state.lock:
        machine_reading = request.app.state.generated_machine_reading

    # return current machine reading?
    if machine_reading is not None and \
        not exceeded_timeframe(
            readable_timestamp, machine_reading.timestamp):
        return {"Value": machine_reading.current,
                "Timestamp": machine_reading.timestamp}

    new_machine_reading = gen_machine_reading(readable_timestamp)

    # store for other request within 1 second:
    async with request.app.state.lock:
        request.app.state.generated_machine_reading = new_machine_reading

    return {"Value": new_machine_reading.current,
            "Timestamp": new_machine_reading.timestamp}


@router.get("/Speed")
async def get_speed(request: Request) -> Dict[str, str | float]:
    """
    Get current Speed from the Maschine Reading.
    New Machine Reading is generated if a predefined timeframe passed
    (currently 1 second).
    """
    # get the current timestamp that binds values together
    current_time: datetime = datetime.now()
    readable_timestamp: str = current_time.strftime(time_format)

    # check the latest generated timestamp
    async with request.app.state.lock:
        machine_reading = request.app.state.generated_machine_reading

    # return current machine reading?
    if machine_reading is not None and \
        not exceeded_timeframe(
            readable_timestamp, machine_reading.timestamp):
        return {"Value": machine_reading.speed,
                "Timestamp": machine_reading.timestamp}

    new_machine_reading = gen_machine_reading(readable_timestamp)

    # store for other request within 1 second:
    async with request.app.state.lock:
        request.app.state.generated_machine_reading = new_machine_reading

    return {"Value": new_machine_reading.speed,
            "Timestamp": new_machine_reading.timestamp}
