import numpy as np
from typing import List, Tuple
import random
import json
import base64

# === Helpers ===
# construct masks:
mask_counter = '011' + 13*'0'
mask_temp = '010' + 13*'0'
mask_data = '000' + 13*'1'


def bitshiftSensors(
        df_x: np.ndarray[tuple[int, ...]],
        df_y: np.ndarray[tuple[int, ...]],
        df_z: np.ndarray[tuple[int, ...]],
        conversion_factors: List[float]) \
        -> Tuple[
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray[tuple[int, ...]]
            ]:
    """
    Given modified vectors:
    - x:  0 counter[MSBx2] x xxxx | xxxx xxxx
    - y:  0 counter[LSBx2] y yyyy | yyyy yyyy
    - z:  0  t           0 z zzzz | zzzz zzzz
    extract the sensor and meta information into seperate data vectors.

    Args:

    Returns:
    - rsx:
    - rsy:
    - rsz:
    - r_temp:
    - r_counter:
    """
    # obtain the counter columns:
    r_col_MSBx2 = df_x & int(mask_counter, 2)
    r_col_LSBx2 = df_y & int(mask_counter, 2)
    r_col_tempB = df_z & int(mask_temp, 2)

    # combine columns:
    r_counter = (r_col_MSBx2 >> 11) | (r_col_LSBx2 >> 13)

    # - special reconstrucion for the temperature -
    # shift out the temperature bits:
    r_temp_col = r_col_tempB >> 14

    # special reconstruction for temperature - interpolation
    # find the first index:
    counter_idx = np.where(r_counter[0:16] == 0)[0][0]
    r_temp = np.zeros_like(r_temp_col)

    for idx16 in range(len(r_temp)//16 - 1):
        # construct indexframe:
        istart = idx16*16 + counter_idx
        istop = (idx16+1)*16 + counter_idx

        # convert back
        bval = r_temp_col[istart:istop].astype(bool)
        temp_value = np.frombuffer(
            np.packbits(bval, bitorder='big'), dtype='>u2')[0]
        r_temp[istart:istop] = temp_value

    r_temp[:counter_idx] = r_temp[counter_idx]
    r_temp[istop:] = r_temp[istart]

    # - obtain sensor data, and convert it -
    r_x = df_x & int(mask_data, 2)
    r_y = df_y & int(mask_data, 2)
    r_z = df_z & int(mask_data, 2)

    rsx = r_x * conversion_factors[0]
    rsy = r_y * conversion_factors[1]
    rsz = r_z * conversion_factors[2]

    # return results:
    return rsx, rsy, rsz, r_temp.astype(float), r_counter


def generate_random_machine_readings() \
        -> Tuple[int, float, float]:
    # generate random values
    value_temperature: int = random.randint(20, 100)
    value_current: float = round(random.uniform(0.0, 100.0), ndigits=3)
    value_speed: float = round(random.uniform(0.0, 5000.0), ndigits=3)

    return value_temperature, value_current, value_speed


# === AAS Utils ===
def get_submodel_element_blob_template():
    """
    Generates a generic template for a Blob Submodel Element.

    Returns:
    - Dict with the template for a Blob Submodel Element
    """
    return {
        "idShort": "",
        "id": "",
        "value": "",
        "semanticId": {
            "type": "ModelReference",
            "keys": [
                {
                    "type": "GlobalReference",
                    "value": "0173-1#02-AAM556#002"
                }
            ]
        },
        "contentType": "application/str",
        "modelType": "Blob"
    }


# Encoding
def encode_dict_to_b64(data_dict: dict) -> str:
    """
    Encodes a dictionary to a base64 string.

    Args:
    - data_dict: The dictionary to encode. Can include floats, ints, strings.

    Returns:
    - base 64 encoded string
    """
    json_str = json.dumps(data_dict)
    json_bytes = json_str.encode('utf-8')
    b64_str = base64.b64encode(json_bytes).decode('utf-8')
    return b64_str
