/// Storage Keys
/// 本地存储键定义
class StorageKeys {
  // ==================== 认证相关 ====================
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String tokenExpiry = 'token_expiry';
  static const String isLoggedIn = 'is_logged_in';

  // ==================== 用户信息 ====================
  static const String userId = 'user_id';
  static const String username = 'username';
  static const String email = 'email';
  static const String userRole = 'user_role';
  static const String role = 'user_role'; // Alias
  static const String userProfile = 'user_profile';
  static const String isActive = 'is_active';

  // ==================== 应用设置 ====================
  static const String themeMode = 'theme_mode'; // light, dark, system
  static const String language = 'language'; // zh, en
  static const String fontSize = 'font_size'; // small, medium, large
  static const String enableNotifications = 'enable_notifications';
  static const String enableSound = 'enable_sound';
  static const String enableVibration = 'enable_vibration';

  // ==================== 答题设置 ====================
  static const String autoNextQuestion = 'auto_next_question';
  static const String showAnswerImmediately = 'show_answer_immediately';
  static const String enableAutoSave = 'enable_auto_save';
  static const String defaultPracticeMode = 'default_practice_mode';

  // ==================== 缓存相关 ====================
  static const String lastSyncTime = 'last_sync_time';
  static const String cachedQuestionBanks = 'cached_question_banks';
  static const String cachedQuestions = 'cached_questions';
  static const String cacheVersion = 'cache_version';

  // ==================== 答题会话 ====================
  static const String currentSessionId = 'current_session_id';
  static const String currentBankId = 'current_bank_id';
  static const String currentQuestionIndex = 'current_question_index';
  static const String sessionState = 'session_state';

  // ==================== 统计数据 ====================
  static const String totalQuestionsAnswered = 'total_questions_answered';
  static const String totalCorrectAnswers = 'total_correct_answers';
  static const String totalStudyTime = 'total_study_time';
  static const String consecutiveDays = 'consecutive_days';
  static const String lastStudyDate = 'last_study_date';

  // ==================== 首次使用 ====================
  static const String isFirstLaunch = 'is_first_launch';
  static const String hasSeenOnboarding = 'has_seen_onboarding';
  static const String appVersion = 'app_version';

  // ==================== AI对话 ====================
  static const String aiChatHistory = 'ai_chat_history';
  static const String aiChatSessionId = 'ai_chat_session_id';
  static const String enableAiAssistant = 'enable_ai_assistant';

  // ==================== 其他 ====================
  static const String lastSelectedBankId = 'last_selected_bank_id';
  static const String favoriteQuestions = 'favorite_questions';
  static const String wrongQuestions = 'wrong_questions';
}
