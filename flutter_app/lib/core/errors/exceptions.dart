/// Base Exception class
/// 所有异常类的基类
class AppException implements Exception {
  final String message;
  final int? statusCode;

  const AppException({
    required this.message,
    this.statusCode,
  });

  @override
  String toString() => 'AppException: $message (Status: $statusCode)';
}

/// Server Exception
/// 服务器异常
class ServerException extends AppException {
  const ServerException({
    required super.message,
    super.statusCode,
  });

  @override
  String toString() => 'ServerException: $message (Status: $statusCode)';
}

/// Network Exception
/// 网络异常
class NetworkException extends AppException {
  const NetworkException({
    super.message = '网络连接失败',
  });

  @override
  String toString() => 'NetworkException: $message';
}

/// Authentication Exception
/// 认证异常
class AuthenticationException extends AppException {
  const AuthenticationException({
    super.message = '认证失败',
    super.statusCode = 401,
  });

  @override
  String toString() => 'AuthenticationException: $message';
}

/// Authorization Exception
/// 权限异常
class AuthorizationException extends AppException {
  const AuthorizationException({
    super.message = '权限不足',
    super.statusCode = 403,
  });

  @override
  String toString() => 'AuthorizationException: $message';
}

/// Not Found Exception
/// 资源不存在异常
class NotFoundException extends AppException {
  const NotFoundException({
    super.message = '资源不存在',
    super.statusCode = 404,
  });

  @override
  String toString() => 'NotFoundException: $message';
}

/// Validation Exception
/// 验证异常
class ValidationException extends AppException {
  final Map<String, List<String>>? errors;

  const ValidationException({
    super.message = '数据验证失败',
    super.statusCode = 422,
    this.errors,
  });

  @override
  String toString() => 'ValidationException: $message, Errors: $errors';
}

/// Cache Exception
/// 缓存异常
class CacheException extends AppException {
  const CacheException({
    super.message = '缓存操作失败',
  });

  @override
  String toString() => 'CacheException: $message';
}

/// Timeout Exception
/// 超时异常
class TimeoutException extends AppException {
  const TimeoutException({
    super.message = '请求超时',
  });

  @override
  String toString() => 'TimeoutException: $message';
}

/// Parse Exception
/// 解析异常
class ParseException extends AppException {
  const ParseException({
    super.message = '数据解析失败',
  });

  @override
  String toString() => 'ParseException: $message';
}

/// Unknown Exception
/// 未知异常
class UnknownException extends AppException {
  const UnknownException({
    super.message = '未知错误',
  });

  @override
  String toString() => 'UnknownException: $message';
}
