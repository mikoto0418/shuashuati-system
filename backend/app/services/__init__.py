"""服务模块初始化"""

from .favorite_service import (  # noqa: F401
    add_favorite,
    favorite_to_dict,
    list_favorites,
    remove_favorite,
)
from .wrong_question_service import (  # noqa: F401
    delete_wrong_question,
    list_wrong_questions,
    wrong_question_to_dict,
)
from .ai_extractor import extract_questions_ai  # noqa: F401
from .user_service import (  # noqa: F401
    change_user_password,
    get_user_settings,
    update_user_ai_settings,
    update_user_preferences,
    update_user_profile,
)
from .dashboard_service import get_dashboard_stats  # noqa: F401
