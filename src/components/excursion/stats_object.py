from typing import Any, Dict, List


class StatsObject:
    def __init__(self, views_num: int = 0, likes_num: int = 0, dislikes_num: int = 0,
                 visitors: List[int] = None) -> None:
        self.views_num = views_num
        self.likes_num = likes_num
        self.dislikes_num = dislikes_num
        self.visitors = list() if visitors is None else visitors

    def get_views_num(self) -> int:
        return self.views_num

    def get_likes_num(self) -> int:
        return self.likes_num

    def get_dislikes_num(self) -> int:
        return self.dislikes_num

    def get_visitors(self) -> List[int]:
        return self.visitors

    def is_completed(self, user_id: int) -> bool:
        return user_id in self.visitors

    def get_unique_visitors_num(self) -> int:
        return len(self.visitors)

    def increase_views_num(self) -> None:
        self.views_num += 1

    def add_new_visitor(self, user_id: int) -> None:
        if user_id not in self.visitors:
            self.visitors.append(user_id)

    def increase_likes_num(self) -> None:
        self.likes_num += 1

    def increase_dislikes_num(self) -> None:
        self.dislikes_num += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "views_num": self.views_num,
            "likes_num": self.likes_num,
            "dislikes_num": self.dislikes_num,
            "visitors": self.visitors,
        }
