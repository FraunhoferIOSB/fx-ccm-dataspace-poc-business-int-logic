from fastapi import APIRouter, Request
from fastapi import UploadFile, File
from fastapi import HTTPException
from datetime import datetime
import pandas as pd  # type: ignore
import io
from typing import List
import logging

# helpers:
from app.routes.utils import bitshiftSensors
from app.datamodels import DemoDataModel, MachineReading, SensorReading

# custom router:
router = APIRouter(prefix='/upload', tags=['upload'])


# === Push Endpoints ===
@router.post("/csv", status_code=204)
async def upload_data_csv(
        request: Request,
        file: UploadFile = File(..., description="demo .csv"),
        ):
    """
    Endpoint to upload DEEPbox files.
    This function parses the DEEPbox file and caches its contents.
    """
    # read data:
    raw_file_content = await file.read()

    # decode csv:
    try:
        df_data: pd.DataFrame = pd.read_csv(
            io.BytesIO(raw_file_content),
            encoding="utf-8",
            sep=';'
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=422,
                            detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid csv: {e}")
        # NOTE: we will remove the error message later

    # - parse out information -
    # NOTE: locations hard coded for now, since the clean configuration will
    #       is to be implemented later!
    # therefore we check the input format
    try:
        assert df_data.iloc[6, 2] == 'PriioSensors_Resolutions', \
            "Wrong Dataframe Format"
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid csv: {e}")

    # get conversion units:
    conversion_factors: List[float] = \
        df_data.iloc[6, 4:7].values.astype(float).tolist()
    conversion_current: float = float(df_data.iloc[6, -2])
    conversion_speed: float = float(df_data.iloc[6, -2])

    # get timestamps-vectors, and compute where the seconds switch:
    timestamps_sec = df_data.iloc[8:, 0].astype(int)
    tiemstamps_nsec = df_data.iloc[8:, 1].astype(int)

    timestamps: List[int] = (
        timestamps_sec*1e+9 + tiemstamps_nsec
    ).tolist()

    try:
        # parse sensor vectors:
        rsx, rsy, rsz, r_temp, _ = bitshiftSensors(
            df_x=df_data.iloc[8:, 4].astype(int).to_numpy(),
            df_y=df_data.iloc[8:, 5].astype(int).to_numpy(),
            df_z=df_data.iloc[8:, 6].astype(int).to_numpy(),
            conversion_factors=conversion_factors
        )
        currents = df_data.iloc[8:, -2].astype(float) * conversion_current
        speeds = df_data.iloc[8:, -1].astype(float) * conversion_speed
        print(f"CSV Parsing successful: {file.filename}")
    except Exception as e:
        raise HTTPException(status_code=501,
                            detail=f"Dataframe Parsing Failed. {e}")

    data = DemoDataModel(
        timestamps=timestamps,
        x=rsx.tolist(),
        y=rsy.tolist(),
        z=rsz.tolist(),
        current=currents.tolist(),
        speed=speeds.tolist(),
        temperature=r_temp.tolist()
    )

    # - get latest datapoint -
    # get a human readable timestamp
    readable_timestamp = datetime.fromtimestamp(timestamps_sec.values[-1]).\
        strftime("%Y-%m-%d %H:%M:%S")
    latest_machine_reading = MachineReading(
        timestamp=readable_timestamp,
        temperature=data.temperature[-1],
        current=data.current[-1],
        speed=data.speed[-1]
    )
    latest_sensor_reading = SensorReading(
        timestamp=readable_timestamp,
        x=data.x[-1],
        y=data.y[-1],
        z=data.z[-1]
    )

    # store/cache:
    async with request.app.state.lock:
        request.app.state.data_cache = data
        # store dedicated datapoints (only latest for now)
        request.app.state.latest_machine_reading = latest_machine_reading
        request.app.state.latest_sensor_reading = latest_sensor_reading

    logging.info(f"CSV uploaded: {file.filename}, entries: {len(data.timestamps)}")
    return
