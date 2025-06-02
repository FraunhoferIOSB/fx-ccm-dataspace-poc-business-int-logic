from typing import Union, Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Query, Response

# data generation functions, aka 'logic'
from app.generatorV2 import generate_DQ, generate_Sensor_A, generate_Sensor_B, create_df, generate_df

app = FastAPI()


class myItem(BaseModel):
    name: str
    rnd:  int

@app.get("/fx/")
def read_root():
    return {"Data Generator for the TP2.04 & TP4.1 POC"}

# quick check of the Query-validation
@app.get("/fx/gen/querydemo")
async def gen_demo(ac:      Annotated[float | None, Query(ge=0., le=2)]    = None, 
                     f_idx:   Annotated[int   | None, Query(ge=0, le=4)]     = None, 
                     s2:      Annotated[float | None, Query(ge=4.2, le=8.5)] = None,
                     error_t: Annotated[int   | None, Query(ge=-1, le=3)]    = None):
    
    """
        Parameters:
        ac      -   Optional, value with with to overwrite the amplitude for frequency at f_idx
        f_idx   -   Optional, identifier for the frequency which will be overwritten
        note: if only ac or f_idx are given, it will be the same as having both of them set to None.
        s2      -   Optional, shift a change in one signal
        error_t -   Optional, 0,1,2 for predefined Error-Types
    """
    # just return the query parameters
    return {"new_amp": ac, "f_idx": f_idx, "signal_switch_2": s2, "error_type": error_t}



@app.get("/fx/gen/units")
def get_gen_units():
    """ Access the units of the dataset directly. """
    return {"Time": "s", "Sensor1": "g", "Sensor2": "g", "DQ1": "rpm", "DQ2": "rpm"}




# generate measurement and receive it as a json:
@app.get("/fx/gen/json")
async def gen_signal_json(ac:      Annotated[float | None, Query(ge=0., le=2)]    = None, 
                     f_idx:   Annotated[int   | None, Query(ge=0, le=4)]     = None, 
                     s2:      Annotated[float | None, Query(ge=4.2, le=8.5)] = None,
                     error_t: Annotated[int   | None, Query(ge=-1, le=3)]    = None):
    
    # generate all the data:
    ds_name, df_gen, error_type = generate_df(ac=ac, f_idx=f_idx, s2_overwrite=s2, error_type=error_t)
    return {"ds_name": ds_name, "new_amp": ac, "f_idx": f_idx, "signal_switch_2": s2, "error_type": error_type, "data": df_gen}


# serve the generated dtaframe as a file
@app.get("/fx/gen/file")
async def gen_signal_file(ac:      Annotated[float | None, Query(ge=0., le=2)]    = None, 
                     f_idx:   Annotated[int   | None, Query(ge=0, le=4)]     = None, 
                     s2:      Annotated[float | None, Query(ge=4.2, le=8.5)] = None,
                     error_t: Annotated[int   | None, Query(ge=-1, le=3)]    = None):
    
    # generate all the data:
    ds_name, df_gen, error_type = generate_df(ac=ac, f_idx=f_idx, s2_overwrite=s2, error_type=error_t)

    # store
    df_gen.to_csv(ds_name + ".csv") 

    # load:
    with open(ds_name + ".csv", "rb") as file:
        df_bin = file.read()

    # return file as body:
    return Response(content=df_bin, media_type="application/octet-stream")