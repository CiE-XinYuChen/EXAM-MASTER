/// API Constants
/// 定义所有API端点和配置
class ApiConstants {
  // Base URL - 根据环境切换
  static const String baseUrl = 'http://127.0.0.1:8000';

  // 生产环境使用局域网IP或域名
  // static const String baseUrl = 'http://192.168.1.100:8000';
  // static const String baseUrl = 'https://api.exam-master.com';

  // API版本
  static const String apiVersion = '/api/v1';
  static const String apiV2 = '/api/v2';
  static const String mcpApi = '/api/mcp';

  // 完整API路径
  static String get apiBaseUrl => '$baseUrl$apiVersion';
  static String get apiV2BaseUrl => '$baseUrl$apiV2';
  static String get mcpBaseUrl => '$baseUrl$mcpApi';

  // 超时配置
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // ==================== 认证相关 ====================
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String refreshToken = '/auth/refresh';
  static const String logout = '/auth/logout';
  static const String currentUser = '/auth/me';

  // ==================== 题库相关 ====================
  static const String questionBanks = '/qbanks';
  static String questionBankDetail(String bankId) => '/qbanks/$bankId';
  static String questionBankQuestions(String bankId) => '/qbanks/$bankId/questions';
  static String questionDetail(String bankId, String questionId) =>
      '/qbanks/$bankId/questions/$questionId';

  // ==================== 答题练习相关 ====================
  static const String practiceSessions = '/practice/sessions';
  static String practiceSessionDetail(String sessionId) => '/practice/sessions/$sessionId';
  static String practiceSessionQuestions(String sessionId) =>
      '/practice/sessions/$sessionId/questions';
  static String practiceSessionNext(String sessionId) =>
      '/practice/sessions/$sessionId/next';
  static String practiceSessionPrevious(String sessionId) =>
      '/practice/sessions/$sessionId/previous';
  static String practiceSessionSubmit(String sessionId) =>
      '/practice/sessions/$sessionId/submit';
  static String practiceSessionComplete(String sessionId) =>
      '/practice/sessions/$sessionId/complete';
  static String practiceSessionResume(String sessionId) =>
      '/practice/sessions/$sessionId/resume';

  // 答题记录
  static const String answerRecords = '/practice/records';
  static String answerRecordDetail(String recordId) => '/practice/records/$recordId';
  static const String answerHistory = '/practice/history';

  // ==================== 统计相关 ====================
  static const String statisticsOverview = '/statistics/overview';
  static const String statisticsDaily = '/statistics/daily';
  static String statisticsDailyByDate(String date) => '/statistics/daily/$date';
  static const String statisticsBanks = '/statistics/banks';
  static String statisticsBankDetail(String bankId) => '/statistics/banks/$bankId';

  // ==================== 收藏相关 ====================
  static const String favorites = '/favorites';
  static String favoriteDetail(String favoriteId) => '/favorites/$favoriteId';
  static String favoriteByQuestion(String questionId) => '/favorites/question/$questionId';
  static const String favoritesCheck = '/favorites/check';
  static const String favoritesBatch = '/favorites/batch';
  static const String favoritesByBank = '/favorites/by-bank';

  // ==================== 错题本相关 ====================
  static const String wrongQuestions = '/wrong-questions';
  static String wrongQuestionDetail(String wrongQuestionId) =>
      '/wrong-questions/$wrongQuestionId';
  static String wrongQuestionByQuestion(String questionId) =>
      '/wrong-questions/question/$questionId';
  static String wrongQuestionCorrect(String wrongQuestionId) =>
      '/wrong-questions/$wrongQuestionId/correct';
  static const String wrongQuestionsAnalysis = '/wrong-questions/analysis';
  static const String wrongQuestionsByBank = '/wrong-questions/by-bank';
  static const String wrongQuestionsBatch = '/wrong-questions/batch';

  // ==================== 激活码相关 ====================
  static const String activationActivate = '/activation/activate';
  static const String activationMyAccess = '/activation/my-access';
  static String activationAccessDetail(String accessId) => '/activation/access/$accessId';

  // ==================== AI对话相关 ====================
  static const String aiChatSessions = '/ai-chat/sessions';
  static String aiChatSessionDetail(String sessionId) => '/ai-chat/sessions/$sessionId';
  static String aiChatSessionMessages(String sessionId) =>
      '/ai-chat/sessions/$sessionId/messages';
  static String aiChatSessionSend(String sessionId) =>
      '/ai-chat/sessions/$sessionId/send';
  static String aiChatSessionClear(String sessionId) =>
      '/ai-chat/sessions/$sessionId/clear';

  // ==================== MCP工具相关 ====================
  static const String mcpTools = '/tools';
  static const String mcpExecute = '/execute';
  static const String mcpBatch = '/batch';

  // ==================== 资源访问 ====================
  static String resourceUrl(String resourceId) => '$baseUrl/resources/$resourceId';

  // ==================== 用户相关 ====================
  static const String userProfile = '/users/me';
  static const String userUpdate = '/users/me';
  static const String userChangePassword = '/users/me/password';
}
