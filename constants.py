import os

# Emojis
LIKE_EMOJI = u"\U0001F44D"  # 👍
DISLIKE_EMOJI = u"\U0001F44E"  # 👎
BLOCK_EMOJI = u"\U0001F6AB"  # 🚫
BACK_ARROW_EMOJI = "\U0001F519"  # 🔙
SMILING_FACE_EMOJI = "\U0001F60A"  # 😊
FOLDED_HANDS_EMOJI = "\U0001F64F"  # 🙏
LOCATION_PIN_EMOJI = "\U0001F4CD"  # 📍
STAR_EMOJI = "\U00002B50"  # ⭐
CONGRATULATIONS_EMOJI = "\U0001F389"  # 🎉
CHECK_MARK_EMOJI = "\U00002705"  # ✅
ERROR_EMOJI = "\U000026A0"  # ⚠️
MAGNIFYING_GLASS_EMOJI = "\U0001F50D"  # 🔍
THINKING_FACE_EMOJI = "\U0001F914"  # 🤔
MONEY_BAG_EMOJI = "\U0001F4B0"  # 💰
STOPWATCH_EMOJI = "\U000023F3"  # ⏳
BOOK_EMOJI = "\U0001F4D6"  # 📖
MIRROR_EMOJI = "\U0001FA9E"  # 🪞
MONEY_SACK_EMOJI = "\U0001F4B0"  # 💰
SYNC_EMOJI = "\U0001F504"  # 🔄

# Paths
USER_STATES_PATH = os.path.abspath("data/user_states.json")
EXCURSIONS_INFO_PATH = os.path.abspath("data/excursions.json")

# User state modes
AUDIO_MODE = "audio"
TEXT_MODE = "text"
AUDIO_MODE_RU = 'аудио формат'
TEXT_MODE_RU = 'текстовый формат'

# Commands
START_COMMAND = 'start'
CHANGE_MODE_COMMAND = 'changemode'
VIEW_EXCURSIONS_COMMAND = 'viewexcursions'

# Errors messages
EXCURSION_DOES_NOT_EXISTS_ERROR = (f"Упс, такой экскурсии не существует!"
                                   f" Может, мы ее потеряли в прошлом веке? {MAGNIFYING_GLASS_EMOJI}")
PAID_EXCURSION_ERROR = f"Эта экскурсия платная. {MONEY_BAG_EMOJI} Купите билет, и мы начнем путешествие!"
INVALID_SELECTION_ERROR = f"Выбор некорректен. Попробуйте снова, ведь мы верим в вас! {THINKING_FACE_EMOJI}"
INVALID_ACTION_ERROR = f"Неправильное действие! Давайте попробуем еще раз. {THINKING_FACE_EMOJI}"
ACCESS_ERROR = f"У вас нет доступа к этой экскурсии. Может, стоит открыть кошелек? {BLOCK_EMOJI}"
AUDIO_IS_NOT_FOUND_ERROR = f"Простите, но аудио для этой точки затерялось где-то в архивах. {DISLIKE_EMOJI}"
DEFAULT_TEXT = "Sorry, text is not provided for this point"
DEFAULT_ADDRESS = "Sorry, address is not provided for this point"

# Default messages
INTRO_NO_ACCESS_MESSAGE = (
    f"{FOLDED_HANDS_EMOJI}{MONEY_BAG_EMOJI}Вы можете насладиться бесплатными пробными экскурсиями или приобрести другие по [ссылке]."
)
WELCOME_MESSAGE = (
    f"Привет! Я ваш Бот-экскурсовод. {LOCATION_PIN_EMOJI} {MIRROR_EMOJI} Вперед к удивительным историям и достопримечательностям!"
)
EXCURSION_START_MESSAGE = f"Приготовьтесь к увлекательному путешествию! {STAR_EMOJI}{STOPWATCH_EMOJI}"
MOVE_ON_REQUEST_MESSAGE = f"Вы закончили осматривать эту локацию? Переходим дальше? {LOCATION_PIN_EMOJI}"
TRANSITION_WARNING_MESSAGE = (
    f"Если вы вернетесь к списку экскурсий, ваш прогресс по текущей экскурсии будет потерян. {ERROR_EMOJI}{BLOCK_EMOJI}\n\n"
    f"Если хотите продолжить, нажмите соответствующую кнопку для экскурсии. {CHECK_MARK_EMOJI}"
)
FEEDBACK_REQUEST_MESSAGE = (
    f"Мы ценим ваше мнение! Как вам экскурсия? {SMILING_FACE_EMOJI}"
)
POSITIVE_FEEDBACK_MESSAGE = f"Рады, что вам понравилось! {LIKE_EMOJI}"
NEGATIVE_FEEDBACK_MESSAGE = f"Сожалеем, что экскурсия не оправдала ожидания. Будем работать лучше! {DISLIKE_EMOJI}"
POSITIVE_FEEDBACK_RESPONSE = f"Спасибо за ваш позитивный отзыв! {STAR_EMOJI}{FOLDED_HANDS_EMOJI}"
NEGATIVE_FEEDBACK_RESPONSE = f"Спасибо за ваш отзыв. Мы обязательно учтем ваши замечания! {FOLDED_HANDS_EMOJI}{THINKING_FACE_EMOJI}"
FEEDBACK_CONGRATS_MESSAGE = (
    f"Поздравляем с завершением экскурсии {{excursion_name}}! {CONGRATULATIONS_EMOJI}{CONGRATULATIONS_EMOJI}\n\n"
    f"Надеемся, вам понравилось. Поделитесь впечатлениями, чтобы мы стали еще лучше! {BOOK_EMOJI}"
)

EXCURSIONS_LIST_MESSAGE = f"Вот список доступных экскурсий. Выбирайте любую и вперед! {LOCATION_PIN_EMOJI}"

# Buttons labels
SYNC_BUTTON = f"Синхронизировать {SYNC_EMOJI}"
MOVE_ON_BUTTON = f"Да, я готов двигаться дальше! {CHECK_MARK_EMOJI}"
VIEW_EXCURSIONS_BUTTON = f"Посмотреть экскурсии {BACK_ARROW_EMOJI}"
START_TOUR_BUTTON = f"Начать экскурсию {STAR_EMOJI}"
IM_HERE_BUTTON = f"Я на месте! {LOCATION_PIN_EMOJI}"
LOVED_IT_BUTTON = f"Очень понравилось! {LIKE_EMOJI}"
COULD_BE_BETTER_BUTTON = f"Могло быть лучше. {DISLIKE_EMOJI}"
CONNECT_TO_VOLK = f"Написать автору"
BACK_TO_EXCURSIONS_BUTTON = f"{BACK_ARROW_EMOJI} Вернуться к экскурсиям"
TRANSITION_CONFIRMATION_BUTTON = f"Хочу перейти к списку {BACK_ARROW_EMOJI}"

# Default settings to excursion labels
DEFAULT_EXCURSION_NAME = "Название засекречено"

# URLs
MESSAGE_TO_VOLK_URL = "https://t.me/ZeevVolk"

# Callback Data Constants
SHOW_EXCURSIONS_CALLBACK = "show_excursions"
DISABLED_CALLBACK = "disabled"
NEXT_POINT_CALLBACK = "next_point"
CHOOSE_CALLBACK = "choose_"
SHOW_EXCURSIONS_SYNC_CALLBACK = "show_excursions_sync"
ARRIVED_CALLBACK = "arrived"
FINISH_CALLBACK = "finish_"
FEEDBACK_CALLBACK = "feedback_"
FEEDBACK_POSITIVE_CALLBACK = "feedback_positive"
FEEDBACK_NEGATIVE_CALLBACK = "feedback_negative"
