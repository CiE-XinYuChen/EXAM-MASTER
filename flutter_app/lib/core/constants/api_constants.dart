/// API Constants
/// 定义所有API端点和配置
class ApiConstants {
  // Environment configuration
  static const bool useProduction = false; // 切换为 false 使用本地开发环境

  // Base URLs
  static const String productionUrl = 'https://exam.shaynechen.tech';
  static const String developmentUrl = 'http://127.0.0.1:8000';

  // Base URL - 根据环境切换
  static String get baseUrl => useProduction ? productionUrl : developmentUrl;

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
  static const String questionBanks = '/qbank/banks';
  static String questionBankDetail(String bankId) => '/qbank/banks/$bankId';
  static const String questionBankQuestions = '/qbank/questions';
  static String questionDetail(String questionId) => '/qbank/questions/$questionId';

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
  static const String userMe = '/users/me'; // Alias for currentUser
  static const String userUpdate = '/users/me';
  static const String userChangePassword = '/users/me/password';

  // Aliases for consistency
  static const String chatSessions = aiChatSessions;
  static String chatSessionById(String sessionId) => aiChatSessionDetail(sessionId);
  static String chatSendMessage(String sessionId) => aiChatSessionSend(sessionId);
  static String chatMessages(String sessionId) => aiChatSessionMessages(sessionId);
  static String favoriteById(String favoriteId) => favoriteDetail(favoriteId);
  static String favoriteCheck(String questionId) => favoriteByQuestion(questionId);
  static String wrongQuestionById(String wrongQuestionId) => wrongQuestionDetail(wrongQuestionId);
  static const String myAccess = activationMyAccess;
  static const String activateCode = activationActivate;
  static String questionBankById(String bankId) => questionBankDetail(bankId);
  static String questionById(String questionId) => questionDetail(questionId);
  static String practiceSessionById(String sessionId) => practiceSessionDetail(sessionId);
  static String practiceSessionHistory(String sessionId) => '${practiceSessionDetail(sessionId)}/history';
  static String practiceSessionPause(String sessionId) => '${practiceSessionDetail(sessionId)}/pause';
  static const String statisticsByBank = statisticsBanks;
  static String statisticsBankById(String bankId) => statisticsBankDetail(bankId);
}
