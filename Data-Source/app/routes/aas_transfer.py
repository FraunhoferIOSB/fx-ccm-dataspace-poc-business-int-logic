from fastapi import APIRouter, Request
from fastapi import UploadFile, File
from fastapi import HTTPException
from datetime import datetime
import pandas as pd  # type: ignore
import io
from typing import List
import uuid
import httpx
import os
import logging

# helpers:
from app.datamodels import DemoDataModel, MachineReading, SensorReading
from app.routes.utils import get_submodel_element_blob_template, \
    encode_dict_to_b64
timeout = 5.0  # seconds
headers = {"Content-Type": "application/json", "Accept": "application/json"}
AAS_SERVER_NETWORK_URL = os.getenv("AAS_SERVER_NETWORK_URL")
if AAS_SERVER_NETWORK_URL is None:
    base_url = "http://<<<address>>>:8000/api/v3.0/"
else:
    base_url = AAS_SERVER_NETWORK_URL

url_motor = f'{base_url}submodels/dXJuOmh0dHBzOi8vdHJ1bXBmLmNvbS9hYXMvc3VibW9kZWwvVGltZVNlcmllcy9Nb3Rvci8wbTAxLzIzNA==/submodel-elements/Segments'
url_getriebe = f'{base_url}submodels/aHR0cHM6Ly93Z3JwLmJpei9zbS9ibG9iLzEvMC94TkE3bVJY/submodel-elements/'

# custom router:
router = APIRouter(prefix='/transfer', tags=['transfer', 'aas', 'aas_transfer'])


@router.get("/blob2aas", status_code=202)
async def upload_blob_to_AAS(request: Request):
    """
    Convert the uploaded data to AAS format and write it to the AAS Server.
    """
    # track elapsed time:
    start_time = datetime.now()

    # get the cached data (blob we want to upload)
    async with request.app.state.lock:
        data = request.app.state.data_cache

    if data is None:
        raise HTTPException(status_code=404, detail="No data available")

    # track loading time
    load_time = datetime.now()

    # - split data into the two corresponding AASs -
    sme_motor = get_submodel_element_blob_template()
    sme_motor["idShort"] = "Blob-Motor-" + str(data.timestamps[0])
    sme_motor["id"] = str(uuid.uuid4())
    sme_motor["contentType"] = 'application/str'

    sme_getriebe = get_submodel_element_blob_template()
    sme_getriebe["idShort"] = "Blob-Getriebe-" + str(data.timestamps[0])
    sme_getriebe["id"] = str(uuid.uuid4())
    sme_getriebe["contentType"] = 'application/str'

    # get values:
    sme_value_motor = {
        "timestamp": data.timestamps,
        "current": data.current,
        "speed": data.speed,
    }
    sme_value_getriebe = {
        "timestamp": data.timestamps,
        "x": data.x,
        "y": data.y,
        "z": data.z,
        "temperature": data.temperature
    }

    # create base64 payload:
    sme_motor["value"] = encode_dict_to_b64(sme_value_motor)
    sme_getriebe["value"] = encode_dict_to_b64(sme_value_getriebe)

    # = load data into the AAS-Server =
    # POST motor data
    logging.info(f"{url_motor}")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            motor_response = await client.post(
                url_motor, json=sme_motor, headers=headers)
            motor_status = motor_response.status_code
            motor_error = motor_response.text if motor_status >= 400 else None
    except httpx.TimeoutException:
        motor_status = 408  # Request Timeout
        motor_error = "Request timeout after 5 seconds"
    except Exception as e:
        motor_status = 500  # Internal Server Error
        motor_error = str(e)

    # POST getriebe data
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            getriebe_response = await client.post(
                url_getriebe, json=sme_getriebe, headers=headers)
            getriebe_status = getriebe_response.status_code
            getriebe_error = getriebe_response.text if getriebe_status >= 400 else None
    except httpx.TimeoutException:
        getriebe_status = 408  # Request Timeout
        getriebe_error = "Request timeout after 5 seconds"
    except Exception as e:
        getriebe_status = 500  # Internal Server Error
        getriebe_error = str(e)

    # elapsed time:
    end_time = datetime.now()
    elapsed_total = (end_time - start_time).total_seconds()
    elapsed_load = (load_time - start_time).total_seconds()

    # return meta information regarding the created submodel elements:
    # 1. submodel elements
    # 2. where they have been created
    # 3. error codes
    user_response = {
        "request-start": str(start_time),
        "load-time": str(elapsed_load) + " seconds",
        "total-time": str(elapsed_total) + " seconds",
        "motor": {
            "name": sme_motor["idShort"],
            "uuid": str(sme_motor["id"]),
            # "values": sme_value_motor,
            "status_code": motor_status,
            **({"error": motor_error} if motor_error else {})
        },
        "getriebe": {
            "name": sme_getriebe["idShort"],
            "uuid": str(sme_getriebe["id"]),
            # "values": sme_value_getriebe,
            "status_code": getriebe_status,
            **({"error": getriebe_error} if getriebe_error else {})
        }
    }

    return user_response
