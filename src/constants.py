import os
from dotenv import load_dotenv

load_dotenv()

# Telegram TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

# Database collections
USER_STATE_COLLECTION = "user"
EXCURSION_COLLECTION = "components"
POINT_COLLECTION = "part"
EXTRA_INFO_COLLECTION = "extraInfo"

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
PLUS_EMOJI = "\u2795"  # ➕
DRAFT_EMOJI = '\U0001F4DD'  # 📝
PUBLISHED_EMOJI = '\U0001F7E2'  # 🟢

# Paths
USER_STATES_PATH = os.path.abspath("data/user_states.json")
EXCURSIONS_INFO_PATH = os.path.abspath("data/excursions.json")
AUDIO_PATH = os.path.abspath("media/audio")
IMAGES_PATH = os.path.abspath("media/images")

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
                                   f" Хм... Напиши мне чтоб я начал ее создавать{MAGNIFYING_GLASS_EMOJI}")
POINT_DOES_NOT_EXISTS_ERROR = f"Упс, такого места в экскурсии не существует... По крайней мере пока"
EXTRA_PART_DOES_NOT_EXISTS_ERROR = f"Упс, такой информации у нас нет..."
PAID_EXCURSION_ERROR = f"Эта экскурсия платная. {MONEY_BAG_EMOJI} Купите билет, и мы начнем путешествие!"
INVALID_SELECTION_ERROR = f"Выбор некорректен. Попробуйте снова, ведь мы верим в вас! {THINKING_FACE_EMOJI}"
INVALID_ACTION_ERROR = f"Неправильное действие! Давайте попробуем еще раз. {THINKING_FACE_EMOJI}"
ACCESS_ERROR = f"У вас нет доступа к этой экскурсии. Может, стоит открыть кошелек? {BLOCK_EMOJI}"
AUDIO_IS_NOT_FOUND_ERROR = f"Простите, но аудио для этой точки затерялось где-то в архивах."
DEFAULT_TEXT = "Тут просто красиво, и я пока еще не придумал, что хочу тут рассказать."
DEFAULT_ADDRESS = "Оглянись вокруг, во всем есть своя красота."

# Default messages
WELCOME_MESSAGE = (
    f"Привет! Я ваш Бот-экскурсовод{LOCATION_PIN_EMOJI}\n"
    f"Думаю нам стоит посмотреть вокруг, насладиться видом и начать знакомиться с тем что я могу предложить."
)
INTRO_ACCESS_MESSAGE = (
    f"{FOLDED_HANDS_EMOJI}{MONEY_BAG_EMOJI}Вы можете насладиться бесплатными пробными экскурсиями"
    f" или приобрести другие просто нажам на них."
)
EXCURSION_START_MESSAGE = f"Приготовьтесь к увлекательному путешествию! {STAR_EMOJI}{STOPWATCH_EMOJI}"
MOVE_ON_REQUEST_MESSAGE = f"Вы закончили осматривать эту локацию? Переходим дальше? {LOCATION_PIN_EMOJI}"
TRANSITION_WARNING_MESSAGE = (
    f"Если вы вернетесь к списку экскурсий, ваш прогресс по текущей экскурсии будет потерян. {ERROR_EMOJI}{BLOCK_EMOJI}\n\n"
    f"Если хотите продолжить, нажмите соответствующую кнопку для экскурсии. {CHECK_MARK_EMOJI}"
)
FEEDBACK_REQUEST_MESSAGE = (
    f"Меня зовут Зеев – я гид, а меня зовут Ваня – я создатель бота, и мы ценим ваше мнение! Как вам экскурсия?{SMILING_FACE_EMOJI}"
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

CHOOSE_EXCURSION_TO_PUBLISH_MESSAGE = "Выберите из списка экскурсию, которую вы хотите опубликовать/скрыть:"
ACTION_COMPLETED_SUCCESFULLY_MESSAGE = f"Действие успешно выполнено {CONGRATULATIONS_EMOJI}"
CURRENT_FIELD_VALUE = "Текущее значение:"
EDIT_POINTS_MESSAGE = "Выберите точку для редактирования или добавьте новую:"
EDIT_POINT_MESSAGE = "Вы редактируете точку: "

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
ADD_EXCURSION_BUTTON = f"{PLUS_EMOJI} Добавить экскурсию"
PUBLISH_EXCURSION_BUTTON = "Опубликовать/Скрыть экскурсию"
EDIT_EXCURSION_BUTTON = f"Редактировать экскурсию"
ADD_POINT_BUTTON = f"{PLUS_EMOJI} Добавить новую точку {LOCATION_PIN_EMOJI}"
EDIT_POINT_BUTTON = f"Редактировать точку"
WRITE_TO_DEVELOPER_BUTTON = "Сообщить об ошибке"
YES_BUTTON = 'Да'
NO_BUTTON = 'Нет'
SKIP_FIELD_BUTTON = 'Пропустить поле'
EDIT_POINTS_BUTTON = 'Редактировать точки'
CHANGE_POINTS_ORDER_BUTTON = 'Редактировать порядок'

# Default settings to components labels
DEFAULT_EXCURSION_NAME = "Название засекречено"
DEFAULT_INFORMATION_PART_NAME = "Секретная программа"

# URLs
MESSAGE_TO_VOLK_URL = "https://t.me/ZeevVolk"
MESSAGE_TO_DEVELOPER_URL = "https://t.me/ivanezox"

# Fields messages
EXCURSION_NAME_FIELD_MESSAGE = "Название экскурсии"
EXCURSION_PAYMENT_REQUIREMENT_FIELD_MESSAGE = "Платная экскурсия"

INFORMATION_PART_NAME_FIELD_MESSAGE = "Название точки/отрывка"
INFORMATION_PART_LINK_FIELD_MESSAGE = "Введите ссылку (если ссылки нет, то введите \"-\""
INFORMATION_PART_AUDIO_FIELD_MESSAGE = "Пришлите файл с аудио"
INFORMATION_PART_TEXT_FIELD_MESSAGE = "Введите текст"
INFORMATION_PART_PHOTOS_FIELD_MESSAGE = "Пришлите фотографии"
POINT_ADDRESS_FIELD_MESSAGE = "Введите адресс локации"
POINT_LOCATION_PHOTO_FIELD_MESSAGE = "Пришлите фото геолокации"

# Fields keys
NAME_FIELD = "name"
# Excursion
EXCURSION_IS_PAID_FIELD = "is_paid"
# Information part
INFORMATION_PART_TEXT_FIELD = "text"
INFORMATION_PART_PHOTOS_FIELD = "photos"
INFORMATION_PART_AUDIO_FIELD = "audio"
INFORMATION_PART_LINK_FIELD = "link"
# Point
POINT_ADDRESS_FIELD = "address"
POINT_LOCATION_PHOTO_FIELD = "location_photo"
POINT_EXTRA_INFORMATION_PART_FIELD = "extra_information_points"

# Types
PHOTO_TYPE = "photos"
AUDIO_TYPE = "audio"

# get_fields() keys
FIELD_MESSAGE_KEY = "field_message"
FIELD_TYPE_KEY = "field_type"
FIELD_NAME_KEY = "field_name"

# Callbacks
SHOW_EXCURSIONS_CALLBACK = "show_excursions"
DISABLED_CALLBACK = "disabled"
NEXT_POINT_CALLBACK = "next_point"
EXTRA_PART_CALLBACK = "extra_"
CHOOSE_CALLBACK = "choose_"
SHOW_EXCURSIONS_SYNC_CALLBACK = "show_excursions_sync"
ARRIVED_CALLBACK = "arrived"
FINISH_CALLBACK = "finish_"
FEEDBACK_CALLBACK = "feedback_"
FEEDBACK_POSITIVE_CALLBACK = "feedback_positive"
FEEDBACK_NEGATIVE_CALLBACK = "feedback_negative"

# Admin Callbacks
PUBLISH_EXCURSION_CALLBACK = "publish_excursion"
PUBLISH_CHOSEN_EXCURSION_CALLBACK = "publish_chosen_excursion_"
ADD_EXCURSION_CALLBACK = "add_excursion"
BOOLEAN_FIELD_CALLBACK = "boolean_"
SKIP_FIELD_CALLBACK = "skip_field"
EDIT_EXCURSION_CALLBACK = "edit_excursion_"
ADD_POINT_CALLBACK = "add_point"
EDIT_POINT_CALLBACK = "edit_point_"
EDIT_POINTS_CALLBACK = "edit_points"
ADD_EXTRA_INFORMATION_CALLBACK = "add_extra_information"
EDIT_EXTRA_INFORMATION_CALLBACK = "edit_extra_information_"
CHANGE_POINTS_ORDER_CALLBACK = "change_points_order"
EDIT_POINT_FIELDS_CALLBACK = "edit_point_fields_"
