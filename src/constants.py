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
EDITING_EMOJI = "\u270F\uFE0F"  # 🖊️ (Pencil for editing)
SKIP_EMOJI = "\u23E9"  # ⏩ (Fast-forward)
CHANGE_ORDER_EMOTIONS = "\U0001F522"  # 🔢 (Input Numbers)
PERSON_EMOJI = "\U0001F464"  # 👤 (Bust in Silhouette)
DELETE_EMOJI = '\U0001F5D1'  # 🗑️
AUTHOR_EMOJI = '\U0001F47D'  # 👽
STATS_EMOJI = '\U0001F4C8'
SUMMARY_EMOJI = '\U0001F4D6'
SUB_THEME_EMOJI = '\U0001F9E9'  # 🧩
FOLDER_EMOJI = '\U0001F4C1'  # 📁
NUMBER_0_EMOJI = '\U00000030\U000020E3'  # 0️⃣
NUMBER_1_EMOJI = '\U00000031\U000020E3'  # 1️⃣
NUMBER_2_EMOJI = '\U00000032\U000020E3'  # 2️⃣
NUMBER_3_EMOJI = '\U00000033\U000020E3'  # 3️⃣
NUMBER_4_EMOJI = '\U00000034\U000020E3'  # 4️⃣
MAP_EMOJI = '\U0001F5FA'  # 🗺️
LINK_EMOJI = "\U0001F517"  # 🔗
PHOTO_EMOJI = "\U0001F4F8"  # 📸
AUDIO_EMOJI = "\U0001F3A7"  # 🎧
TEXT_EMOJI = "\U0001F4AC"  # 💬
QUESTION_EMOJI = "\U00002753"  # ❓
CURRENT_STATE_EMOJI = "\U000026F3"  # ⛳
FINISH_EMOJI = "\U0001F3C1"  # 🏁

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
    f" или приобрести другие просто нажав на них."
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

ACTION_COMPLETED_SUCCESSFULLY_MESSAGE = f"Действие успешно выполнено {CONGRATULATIONS_EMOJI}"
CURRENT_FIELD_VALUE = f"{CURRENT_STATE_EMOJI} Текущее значение:"
EDIT_POINTS_MESSAGE = f"{FOLDER_EMOJI}{LOCATION_PIN_EMOJI} Выберите точку для редактирования или добавьте новую:"
EDIT_POINT_MESSAGE = f"{FOLDER_EMOJI}{LOCATION_PIN_EMOJI} Вы редактируете точку: "
EDIT_EXTRA_POINT_MESSAGE = f"{FOLDER_EMOJI}{SUB_THEME_EMOJI} Вы редактируете подтему: "
CHANGING_ORDER_MESSAGE = ("Вы редактируете порядок точек в экскурсии.\nПожалуйста, введите номера точек через запятую"
                          " и отправьте сообщение\n"
                          "Пример: 1, 4, 5, 6")
WRONG_FORMAT_MESSAGE = f"{ERROR_EMOJI} Неправильный формат, попробуйте еще раз"

# Buttons labels
SYNC_BUTTON = f"Синхронизировать {SYNC_EMOJI}"
MOVE_ON_BUTTON = f"Да, я готов двигаться дальше! {CHECK_MARK_EMOJI}"
VIEW_EXCURSIONS_BUTTON = f"Посмотреть экскурсии {BACK_ARROW_EMOJI}"
START_TOUR_BUTTON = f"Начать экскурсию {STAR_EMOJI}"
IM_HERE_BUTTON = f"Я на месте! {LOCATION_PIN_EMOJI}"
LOVED_IT_BUTTON = f"Очень понравилось! {LIKE_EMOJI}"
COULD_BE_BETTER_BUTTON = f"Могло быть лучше. {DISLIKE_EMOJI}"
CONNECT_TO_VOLK = f"{AUTHOR_EMOJI} Написать автору"
BACK_TO_EXCURSIONS_BUTTON = f"{BACK_ARROW_EMOJI} Вернуться к экскурсиям"
TRANSITION_CONFIRMATION_BUTTON = f"Хочу перейти к списку {BACK_ARROW_EMOJI}"
ADD_EXCURSION_BUTTON = f"{PLUS_EMOJI} Добавить экскурсию"
PUBLISH_EXCURSION_BUTTON = f"{PUBLISHED_EMOJI} Опубликовать / {DRAFT_EMOJI} Скрыть экскурсию"
EDIT_EXCURSION_BUTTON = f"{EDITING_EMOJI} Редактировать экскурсию"
ADD_POINT_BUTTON = f"{PLUS_EMOJI} Добавить новую точку {LOCATION_PIN_EMOJI}"
ADD_EXTRA_POINT_BUTTON = f"{PLUS_EMOJI} Добавить подтему {SUB_THEME_EMOJI}"
EDIT_EXTRA_POINT_BUTTON = f"{EDITING_EMOJI} Редактировать подтему {SUB_THEME_EMOJI}"
EDIT_POINT_BUTTON = f"{EDITING_EMOJI} Редактировать точку {LOCATION_PIN_EMOJI}"
WRITE_TO_DEVELOPER_BUTTON = f"{ERROR_EMOJI} Сообщить об ошибке"
OPEN_LOCATION_IN_GOOGLE_MAPS = f"{MAP_EMOJI} Открыть в Google Maps"
YES_BUTTON = 'Да'
NO_BUTTON = 'Нет'
SKIP_FIELD_BUTTON = f'{SKIP_EMOJI} Пропустить поле'
EDIT_POINTS_BUTTON = f'{EDITING_EMOJI} Редактировать точки {LOCATION_PIN_EMOJI}{LOCATION_PIN_EMOJI}{LOCATION_PIN_EMOJI}'
CHANGE_POINTS_ORDER_BUTTON = f'{CHANGE_ORDER_EMOTIONS} Редактировать порядок'
DELETE_POINT_BUTTON = f"{DELETE_EMOJI} Удалить точку"
DELETE_EXTRA_POINT_BUTTON = f"{DELETE_EMOJI} Удалить подтему"
EXCURSION_STATS_BUTTON = f"{STATS_EMOJI} Статистика"
EXCURSION_SUMMARY_BUTTON = f"{SUMMARY_EMOJI} Обзор экскурсии"
DELETE_EXCURSION_BUTTON = f"{DELETE_EMOJI} Удалить экскурсию"
DISABLE_SENDING_FILES_BUTTON = f"{FINISH_EMOJI} Закончить отправку файлов"
RETURN_TO_PREVIOUS_MENU_STATE = f"{BACK_ARROW_EMOJI} Вернуться обратно"

# Default settings to components labels
DEFAULT_EXCURSION_NAME = "Название засекречено"
DEFAULT_INFORMATION_PART_NAME = "Секретная программа"

# URLs
MESSAGE_TO_VOLK_URL = "https://t.me/ZeevVolk"
MESSAGE_TO_DEVELOPER_URL = "https://t.me/ivanezox"

# Fields messages
EXCURSION_NAME_FIELD_MESSAGE = f"{TEXT_EMOJI} Введите название экскурсии. Если хотите оставить предыдущее значение, пропустите поле"
EXCURSION_PAYMENT_REQUIREMENT_FIELD_MESSAGE = f"{QUESTION_EMOJI} Платная экскурсия?"

INFORMATION_PART_NAME_FIELD_MESSAGE = (f"{TEXT_EMOJI} Введите (пришлите сообщение) название точки/отрывка. "
                                       "Если хотите оставить предыдущее значение, пропустите поле")
INFORMATION_PART_LINK_FIELD_MESSAGE = f"{LINK_EMOJI} Введите ссылку (если ссылки нет, то пропустите это поле)"
INFORMATION_PART_AUDIO_FIELD_MESSAGE = f"{AUDIO_EMOJI} Пришлите файлы с аудио. Если хотите оставить предыдущее значение, пропустите поле"
INFORMATION_PART_TEXT_FIELD_MESSAGE = f"{TEXT_EMOJI} Введите текст. Если хотите оставить предыдущее значение, пропустите поле"
INFORMATION_PART_PHOTOS_FIELD_MESSAGE = f"{PHOTO_EMOJI} Пришлите фотографии. Если хотите оставить предыдущее значение, пропустите поле"
POINT_ADDRESS_FIELD_MESSAGE = f"{TEXT_EMOJI} Введите адресс локации. Если хотите оставить предыдущее значение, пропустите поле"
POINT_LOCATION_PHOTO_FIELD_MESSAGE = f"{PHOTO_EMOJI} Пришлите фото геолокации. Если хотите оставить предыдущее значение, пропустите поле"
POINT_LOCATION_LINK_FIELD_MESSAGE = f"{LINK_EMOJI} Пришлите ссылку на точку в Google Maps. Если хотите оставить предыдущее значение, пропустите поле"

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
POINT_LOCATION_LINK_FIELD = "location_link"

# Types
PHOTO_TYPE = "photos"
AUDIO_TYPE = "audio"
ONE_PHOTO_TYPE = "photo"

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
EDIT_EXTRA_POINT_CALLBACK = "edit_extra_point_"
EDIT_POINTS_CALLBACK = "edit_points"
DELETE_POINT_CALLBACK = "delete_point_"
CHANGE_POINTS_ORDER_CALLBACK = "change_points_order"
EDIT_POINT_FIELDS_CALLBACK = "edit_point_fields_"
ADD_EXTRA_POINT_CALLBACK = "add_extra_point_"
EDIT_EXTRA_POINT_FIELDS_CALLBACK = "edit_fields_extra_point_"
DELETE_EXTRA_POINT_CALLBACK = "delete_extra_point_"
DELETE_EXCURSION_CALLBACK = "delete_excursion"
EXCURSION_STATS_CALLBACK = "excursion_stats"
EXCURSION_SUMMARY_CALLBACK = "excursion_summary"
DISABLE_SENDING_FILES_CALLBACK = "disable_sending_files"
