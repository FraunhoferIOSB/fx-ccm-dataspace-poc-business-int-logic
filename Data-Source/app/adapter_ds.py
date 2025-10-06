from fastapi import FastAPI

# custom routing:
from app.routes import GenRouter, GetRouter, UploadRouter, \
    AASTransferRouter

# context management:
from contextlib import asynccontextmanager
import anyio


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.lock = anyio.Lock()
    app.state.latest_machine_reading = None
    app.state.latest_sensor_reading = None
    app.state.data_cache = None
    # dummy:
    app.state.generated_machine_reading = None
    yield
    # - No Teardown


# === App ===
app = FastAPI(
    title="Minimal Adapter (Data-Source) Demo",
    version="0.0.4",
    lifespan=lifespan)


# === General-Endpoints ===
@app.get("/fx")
def read_root():
    return "Data Generator k8s Deployment"


# === further Routing ===
app.include_router(GenRouter, prefix="/fx")
app.include_router(GetRouter, prefix="/fx")
app.include_router(UploadRouter, prefix="/fx")
app.include_router(AASTransferRouter, prefix="/fx")
