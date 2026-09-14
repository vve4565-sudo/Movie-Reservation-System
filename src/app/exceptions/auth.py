class UserNotExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WrongPassword(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserAlreadyExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
