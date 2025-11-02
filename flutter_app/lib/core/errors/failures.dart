import 'package:equatable/equatable.dart';

/// Base Failure class
/// 所有失败类的基类
abstract class Failure extends Equatable {
  final String message;
  final int? statusCode;

  const Failure({
    required this.message,
    this.statusCode,
  });

  @override
  List<Object?> get props => [message, statusCode];
}

/// Server Failure
/// 服务器错误
class ServerFailure extends Failure {
  const ServerFailure({
    required super.message,
    super.statusCode,
  });
}

/// Network Failure
/// 网络连接错误
class NetworkFailure extends Failure {
  const NetworkFailure({
    super.message = '网络连接失败，请检查网络设置',
  });
}

/// Authentication Failure
/// 认证失败
class AuthenticationFailure extends Failure {
  const AuthenticationFailure({
    super.message = '认证失败，请重新登录',
    super.statusCode = 401,
  });
}

/// Authorization Failure
/// 权限不足
class AuthorizationFailure extends Failure {
  const AuthorizationFailure({
    super.message = '权限不足',
    super.statusCode = 403,
  });
}

/// Not Found Failure
/// 资源不存在
class NotFoundFailure extends Failure {
  const NotFoundFailure({
    super.message = '请求的资源不存在',
    super.statusCode = 404,
  });
}

/// Validation Failure
/// 数据验证失败
class ValidationFailure extends Failure {
  final Map<String, List<String>>? errors;

  const ValidationFailure({
    super.message = '数据验证失败',
    super.statusCode = 422,
    this.errors,
  });

  @override
  List<Object?> get props => [message, statusCode, errors];
}

/// Cache Failure
/// 缓存错误
class CacheFailure extends Failure {
  const CacheFailure({
    super.message = '缓存操作失败',
  });
}

/// Timeout Failure
/// 请求超时
class TimeoutFailure extends Failure {
  const TimeoutFailure({
    super.message = '请求超时，请重试',
  });
}

/// Unknown Failure
/// 未知错误
class UnknownFailure extends Failure {
  const UnknownFailure({
    super.message = '未知错误',
  });
}

/// Parse Failure
/// 数据解析失败
class ParseFailure extends Failure {
  const ParseFailure({
    super.message = '数据解析失败',
  });
}
