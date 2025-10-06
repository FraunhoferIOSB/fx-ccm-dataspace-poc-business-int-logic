from .generators import router as GenRouter
from .getdata import router as GetRouter
from .upload import router as UploadRouter
from .aas_transfer import router as AASTransferRouter

__all__ = [
    "GenRouter",
    "GetRouter",
    "UploadRouter",
    "AASTransferRouter"
]
