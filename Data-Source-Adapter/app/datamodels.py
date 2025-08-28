from pydantic import BaseModel, Field
from typing import List


# === Data-Models ===
# data persistence - temp, in memory
class MachineReading(BaseModel):
    """
    Data Model for the Maschine Readings.
    """
    timestamp: str

    # machine-data:
    temperature: float
    current: float
    speed: float


class SensorReading(BaseModel):
    """
    Data Model for the Acceleration Sensors.
    """
    timestamp: str

    # accel.-sensor data:
    x: float
    y: float
    z: float


class DemoDataModel(BaseModel):
    """
    Data-Model to Cahce the given DataFrame.
    """
    timestamps: List[int] = Field(..., description="Timestamps in [ns]")
    x: List[float] = Field(..., description='Sensor-Data-X')
    y: List[float] = Field(..., description='Sensor-Data-Y')
    z: List[float] = Field(..., description='Sensor-Data-Z')

    current: List[float] = Field(..., description='Motor Current')
    speed: List[float] = Field(..., description='Velocity')
    temperature: List[float] = Field(..., description='Temperature')
