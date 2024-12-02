from excursion import Excursion
from constants import TEXT_MODE, AUDIO_MODE, AUDIO_MODE_RU, TEXT_MODE_RU


class UserState:
    """Tracks the state of an individual user."""

    def __init__(self, username: str, user_id: int, mode: str = TEXT_MODE, paid_excursions: list[str] = None,
                 completed_excursions: list[str] = None) -> None:
        self.username = username
        self.user_id = user_id
        # self.point_index = 0
        self.mode = mode
        self.current_excursion = None
        self.current_excursion_step = -1
        self.paid_excursions = paid_excursions if paid_excursions is not None else []
        self.completed_excursions = completed_excursions if completed_excursions is not None else []

    def change_mode(self) -> None:
        self.mode = AUDIO_MODE if self.mode == TEXT_MODE else TEXT_MODE

    def get_username(self) -> str:
        return self.username

    def set_excursion(self, excursion: Excursion) -> None:
        self.current_excursion = excursion

    def does_have_access(self, excursion: Excursion) -> bool:
        if excursion.get_name() in self.paid_excursions:
            return True
        return False

    def is_excursion_completed(self, excursion: Excursion) -> bool:
        if excursion.get_name() in self.completed_excursions:
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
        print()
        self.completed_excursions.append(excursion.get_name())

    def add_paid_excursion(self, excursion: Excursion) -> None:
        self.paid_excursions.append(excursion.get_name())

    def get_mode(self) -> str:
        return AUDIO_MODE_RU if self.mode == TEXT_MODE else TEXT_MODE_RU

    def to_dict(self):
        """Convert the user state to a dictionary for JSON serialization."""
        return {
            "username": self.username,
            "user_id": self.user_id,
            # "point_index": self.point_index,
            "mode": self.mode,
            "paid_excursions": self.paid_excursions,
            "completed_excursions": self.completed_excursions
        }
