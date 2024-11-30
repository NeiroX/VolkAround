from excursion import Excursion
from constants import TEXT_MODE, AUDIO_MODE, AUDIO_MODE_RU, TEXT_MODE_RU


class UserState:
    """Tracks the state of an individual user."""

    def __init__(self, username: str, user_id: int):
        self.username = username
        self.user_id = user_id
        self.point_index = 0
        self.mode = TEXT_MODE
        self.current_excursion = None
        self.current_excursion_step = -1
        self.paid_excursions = list()
        self.completed_excursions = list()

    def change_mode(self) -> None:
        self.mode = AUDIO_MODE if self.mode == TEXT_MODE else TEXT_MODE

    def get_user_name(self) -> str:
        return self.username

    def set_excursion(self, excursion: Excursion) -> None:
        self.current_excursion = excursion

    def does_have_access(self, excursion: Excursion) -> bool:
        if excursion in self.paid_excursions:
            return True
        return False

    def is_excursion_completed(self, excursion: Excursion) -> bool:
        if excursion in self.completed_excursions:
            return True
        return False

    def reset_current_excursion(self) -> None:
        self.current_excursion = None
        self.current_excursion_step = -1

    def get_current_excursion(self) -> Excursion:
        return self.current_excursion

    def get_current_excursion_step(self) -> int:
        return self.current_excursion_step

    def get_point(self):
        return self.current_excursion.get_point(self.current_excursion_step)

    def excursion_next_step(self) -> None:
        self.current_excursion_step += 1

    def get_user_id(self) -> int:
        return self.user_id

    def add_completed_excursion(self, excursion: Excursion) -> None:
        self.completed_excursions.append(excursion)

    def add_paid_excursion(self, excursion: Excursion) -> None:
        self.paid_excursions.append(excursion)

    def get_mode(self) -> str:
        return AUDIO_MODE_RU if self.mode == TEXT_MODE else TEXT_MODE_RU
