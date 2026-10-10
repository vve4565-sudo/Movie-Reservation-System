class ReservationNotExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ReservationAlredyExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ChairAndShowNotMatched(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
