from src.components.excursion.excursion import Excursion
from src.components.user.user_editor import UserEditor
from src.constants import TEXT_MODE, AUDIO_MODE, AUDIO_MODE_RU, TEXT_MODE_RU


class UserState:
    """Tracks the state of an individual user."""

    def __init__(self, username: str, user_id: int, mode: str = TEXT_MODE, paid_excursions: list[int] = None,
                 completed_excursions: list[int] = None, is_admin: bool = False) -> None:
        self.username = username
        self.user_id = user_id
        self.is_admin = is_admin
        self.mode = mode
        self.current_excursion = None
        self.current_excursion_step = -1
        self.paid_excursions = paid_excursions if paid_excursions is not None else []
        self.user_editor = UserEditor()

    def change_mode(self) -> None:
        print("Current user mode: ", self.mode)
        self.mode = AUDIO_MODE if self.mode == TEXT_MODE else TEXT_MODE

    def get_username(self) -> str:
        return self.username

    def set_excursion(self, excursion: Excursion) -> None:
        self.current_excursion = excursion

    def does_have_access(self, excursion: Excursion) -> bool:
        if self.is_admin or excursion.get_id() in self.paid_excursions:
            return True
        return False

    def does_have_admin_access(self) -> bool:
        return self.is_admin

    def is_excursion_completed(self, excursion: Excursion) -> bool:
        if excursion.get_id() in self.completed_excursions:
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

    def add_paid_excursion(self, excursion: Excursion) -> None:
        self.paid_excursions.append(excursion.get_id())

    def get_mode(self) -> str:
        return AUDIO_MODE_RU if self.mode == AUDIO_MODE else TEXT_MODE_RU

    def to_dict(self):
        """Convert the user state to a dictionary for JSON serialization."""
        return {
            "username": self.username,
            "user_id": self.user_id,
            "mode": self.mode,
            "is_admin": self.is_admin,
            "paid_excursions": self.paid_excursions,
        }
