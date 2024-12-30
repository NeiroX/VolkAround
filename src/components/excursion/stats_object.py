from typing import Any, Dict


class StatsObject:
    def __init__(self, visitors_num: int = 0, likes_num: int = 0, dislikes_num: int = 0) -> None:
        self.visitors_num = visitors_num
        self.likes_num = likes_num
        self.dislikes_num = dislikes_num

    def get_visitors_num(self) -> int:
        return self.visitors_num

    def get_likes_num(self) -> int:
        return self.likes_num

    def get_dislikes_num(self) -> int:
        return self.dislikes_num

    def increase_visitors_num(self) -> None:
        self.visitors_num += 1

    def increase_likes_num(self) -> None:
        self.likes_num += 1

    def increase_dislikes_num(self) -> None:
        self.dislikes_num += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "visitors_num": self.visitors_num,
            "likes_num": self.likes_num,
            "dislikes_num": self.dislikes_num,
        }
