from excursion import Excursion


class UserState:
    """Tracks the state of an individual user."""

    def __init__(self, username: str, user_id: int):
        self.username = username
        self.user_id = user_id
        self.point_index = 0
        self.mode = "text"
        self.current_excursion = None
        self.has_paid_access = False  # Set to True for paid users
        self.paid_excursions = list()
        self.completed_excursions = list()

    def change_mode(self, mode: str):
        self.mode = mode

    def get_user_name(self):
        return self.username

    def does_have_access(self, excursion: Excursion) -> bool:
        if excursion in self.paid_excursions:
            return True
        return False

    def is_excursion_completed(self, excursion: Excursion) -> bool:
        if excursion in self.completed_excursions:
            return True
        return False

    def get_user_id(self):
        return self.user_id

    def add_completed_excursion(self, excursion: Excursion):
        self.completed_excursions.append(excursion)

    def add_paid_excursion(self, excursion: Excursion):
        self.paid_excursions.append(excursion)

    def get_mode(self):
        return self.mode
