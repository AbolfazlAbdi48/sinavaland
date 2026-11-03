from imagekit import ImageSpec
from imagekit.processors import (
    ResizeToFill,
    ResizeToFit,
    Transpose,
)


class ThumbnailSpec(ImageSpec):
    processors = [
        Transpose(),
        ResizeToFill(180, 180),
    ]
    format = "WEBP"
    options = {"quality": 80}


class CardImageSpec(ImageSpec):
    processors = [
        Transpose(),
        ResizeToFill(468, 468),
    ]
    format = "WEBP"
    options = {"quality": 82}


class LargeImageSpec(ImageSpec):
    processors = [
        Transpose(),
        ResizeToFit(1024, 1024),
    ]
    format = "WEBP"
    options = {"quality": 85}


class HeroImageSpec(ImageSpec):
    processors = [Transpose(), ResizeToFill(1600, 700)]
    format = "WEBP"
    options = {"quality": 85}


class HomeCardLargeSpec(ImageSpec):
    processors = [
        Transpose(),
        ResizeToFill(960, 960),
    ]
    format = "WEBP"
    options = {"quality": 85}
