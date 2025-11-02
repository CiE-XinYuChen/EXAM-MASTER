/// App Constants
/// 应用级常量定义
class AppConstants {
  // 应用信息
  static const String appName = 'EXAM MASTER';
  static const String appVersion = '1.0.0';
  static const String appDescription = '智能题库学习系统';

  // 分页配置
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // 缓存配置
  static const Duration cacheExpiration = Duration(hours: 24);
  static const Duration imageCacheExpiration = Duration(days: 7);
  static const int maxCacheSize = 100 * 1024 * 1024; // 100MB

  // 答题配置
  static const int autoSaveInterval = 30; // 秒
  static const int questionCardPreloadCount = 3; // 预加载题目数量

  // 多媒体配置
  static const int maxImageSize = 10 * 1024 * 1024; // 10MB
  static const int maxVideoSize = 100 * 1024 * 1024; // 100MB
  static const int maxAudioSize = 20 * 1024 * 1024; // 20MB

  // 题型
  static const String questionTypeSingle = 'single';
  static const String questionTypeMultiple = 'multiple';
  static const String questionTypeJudge = 'judge';
  static const String questionTypeFill = 'fill';
  static const String questionTypeEssay = 'essay';

  // 难度
  static const String difficultyEasy = 'easy';
  static const String difficultyMedium = 'medium';
  static const String difficultyHard = 'hard';
  static const String difficultyExpert = 'expert';

  // 答题模式
  static const String practiceModeSequential = 'sequential'; // 顺序
  static const String practiceModeRandom = 'random'; // 随机
  static const String practiceModeWrong = 'wrong_only'; // 错题
  static const String practiceModeFavorite = 'favorite_only'; // 收藏
  static const String practiceModeUnpracticed = 'unpracticed'; // 未练习

  // 会话状态
  static const String sessionStatusInProgress = 'in_progress';
  static const String sessionStatusCompleted = 'completed';
  static const String sessionStatusPaused = 'paused';

  // 日期格式
  static const String dateFormat = 'yyyy-MM-dd';
  static const String dateTimeFormat = 'yyyy-MM-dd HH:mm:ss';
  static const String timeFormat = 'HH:mm:ss';

  // 错误消息
  static const String errorNetworkConnection = '网络连接失败，请检查网络设置';
  static const String errorServerError = '服务器错误，请稍后重试';
  static const String errorUnauthorized = '未授权，请重新登录';
  static const String errorNotFound = '请求的资源不存在';
  static const String errorTimeout = '请求超时，请重试';
  static const String errorUnknown = '未知错误';

  // 成功消息
  static const String successLogin = '登录成功';
  static const String successRegister = '注册成功';
  static const String successLogout = '退出成功';
  static const String successSubmit = '提交成功';
  static const String successSave = '保存成功';
  static const String successDelete = '删除成功';

  // 正则表达式
  static final RegExp emailRegex = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );
  static final RegExp usernameRegex = RegExp(
    r'^[a-zA-Z0-9_]{3,20}$',
  );
  static final RegExp passwordRegex = RegExp(
    r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$',
  );

  // 主题颜色
  static const int primaryColorValue = 0xFF667EEA;
  static const int secondaryColorValue = 0xFF764BA2;
  static const int accentColorValue = 0xFF4CAF50;
  static const int errorColorValue = 0xFFF44336;
  static const int warningColorValue = 0xFFFF9800;
  static const int successColorValue = 0xFF4CAF50;
}
