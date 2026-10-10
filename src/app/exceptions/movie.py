class ImageSaveError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidImageExtensionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MovieImageNotExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MovieNotExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
