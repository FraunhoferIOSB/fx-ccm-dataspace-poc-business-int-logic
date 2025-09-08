from .generators import router as GenRouter
from .getdata import router as GetRouter
from .upload import router as UploadRouter

__all__ = [
    "GenRouter",
    "GetRouter",
    "UploadRouter"
]
