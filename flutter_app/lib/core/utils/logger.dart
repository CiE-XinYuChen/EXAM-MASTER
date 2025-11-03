import 'package:logger/logger.dart';

/// App Logger
/// 应用日志工具
class AppLogger {
  static final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 2,
      errorMethodCount: 8,
      lineLength: 120,
      colors: true,
      printEmojis: true,
      printTime: true,
    ),
  );

  static void d(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.d(message, error: error, stackTrace: stackTrace);
  }

  static void i(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message, error: error, stackTrace: stackTrace);
  }

  static void w(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message, error: error, stackTrace: stackTrace);
  }

  static void e(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message, error: error, stackTrace: stackTrace);
  }

  static void wtf(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _logger.f(message, error: error, stackTrace: stackTrace);
  }

  // Aliases for convenience
  static void debug(dynamic message, [dynamic error, StackTrace? stackTrace]) => d(message, error, stackTrace);
  static void info(dynamic message, [dynamic error, StackTrace? stackTrace]) => i(message, error, stackTrace);
  static void warning(dynamic message, [dynamic error, StackTrace? stackTrace]) => w(message, error, stackTrace);
  static void error(dynamic message, [dynamic error, StackTrace? stackTrace]) => e(message, error, stackTrace);
}
