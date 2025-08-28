from fastapi import APIRouter, Request, HTTPException
from typing import Dict

# helpers:
from app.datamodels import MachineReading, SensorReading

# create router:
router = APIRouter(prefix='/get', tags=['get'])


# --- Current Machine Readings ---
@router.get("/machinereadings", status_code=200, response_model=MachineReading)
async def get_machinereadings(request: Request):
    """
    Get Latest Maschine Readings.

    Args: -
    Returns: JSON with a human readable time stamp and
        machine readings (up to 3rd decimal precision).
    """
    # get the current machine reading
    async with request.app.state.lock:
        machine_reading = request.app.state.latest_machine_reading

    # upload exists?
    if machine_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return machine_reading


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


# --- get latest sensor readings ---
@router.get("/sensorreadings", status_code=200, response_model=SensorReading)
async def get_sensorreadings(request: Request):
    """
    Get Latest Sensor Readings.

    Args: -
    Returns: JSON with a human readable time stamp and
        sensor readings.
    """
    # get the current machine reading
    async with request.app.state.lock:
        sensor_reading = request.app.state.latest_sensor_reading

    # upload exists?
    if sensor_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return sensor_reading


# = dedicated paths =
@router.get("/Temperature", status_code=200)
async def get_temperature(request: Request) -> Dict[str, str | float]:
    """
    Get Temperature from the Maschine Reading.
    """
    # get the current machine reading
    async with request.app.state.lock:
        machine_reading = request.app.state.latest_machine_reading

    # upload exists?
    if machine_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": machine_reading.temperature,
            "Timestamp": machine_reading.timestamp}


@router.get("/Current", status_code=200)
async def get_current(request: Request) -> Dict[str, str | float]:
    """
    Get current Current from the Maschine Reading.
    """
    # get the current machine reading
    async with request.app.state.lock:
        machine_reading = request.app.state.latest_machine_reading

    # upload exists?
    if machine_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": machine_reading.current,
            "Timestamp": machine_reading.timestamp}


@router.get("/Speed")
async def get_speed(request: Request) -> Dict[str, str | float]:
    """
    Get current Current from the Maschine Reading.
    """
    # get the current machine reading
    async with request.app.state.lock:
        machine_reading = request.app.state.latest_machine_reading

    # upload exists?
    if machine_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": machine_reading.speed,
            "Timestamp": machine_reading.timestamp}


@router.get("/sensor/x", status_code=200)
async def get_sensor_x(request: Request) -> Dict[str, str | float]:
    """
    Get Accel.-X from the Sensor Readings.
    """
    # get the current machine reading
    async with request.app.state.lock:
        sensor_reading = request.app.state.latest_sensor_reading

    # upload exists?
    if sensor_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": sensor_reading.x,
            "Timestamp": sensor_reading.timestamp}


@router.get("/sensor/y", status_code=200)
async def get_sensor_y(request: Request) -> Dict[str, str | float]:
    """
    Get Accel.-Y from the Sensor Readings.
    """
    # get the current machine reading
    async with request.app.state.lock:
        sensor_reading = request.app.state.latest_sensor_reading

    # upload exists?
    if sensor_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": sensor_reading.y,
            "Timestamp": sensor_reading.timestamp}


@router.get("/sensor/z", status_code=200)
async def get_sensor_z(request: Request) -> Dict[str, str | float]:
    """
    Get Accel.-Z from the Sensor Readings.
    """
    # get the current machine reading
    async with request.app.state.lock:
        sensor_reading = request.app.state.latest_sensor_reading

    # upload exists?
    if sensor_reading is None:
        raise HTTPException(status_code=404, detail="No data loaded yet.")

    return {"Value": sensor_reading.z,
            "Timestamp": sensor_reading.timestamp}
