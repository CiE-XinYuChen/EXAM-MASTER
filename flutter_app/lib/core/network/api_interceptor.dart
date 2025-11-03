import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../errors/exceptions.dart';
import '../constants/storage_keys.dart';

/// API Interceptor
/// 处理请求/响应拦截、Token注入、错误处理
class ApiInterceptor extends Interceptor {
  final Logger _logger;

  ApiInterceptor(this._logger);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // 自动注入Token
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(StorageKeys.accessToken);
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    _logger.d('REQUEST[${options.method}] => PATH: ${options.path}');
    super.onRequest(options, handler);
  }

  @override
  void onResponse(
    Response response,
    ResponseInterceptorHandler handler,
  ) {
    _logger.d(
      'RESPONSE[${response.statusCode}] => PATH: ${response.requestOptions.path}',
    );
    super.onResponse(response, handler);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) {
    _logger.e(
      'ERROR[${err.response?.statusCode}] => PATH: ${err.requestOptions.path}',
    );

    // 根据错误类型抛出相应的异常
    final exception = _handleError(err);
    handler.reject(
      DioException(
        requestOptions: err.requestOptions,
        error: exception,
        response: err.response,
        type: err.type,
      ),
    );
  }

  /// 处理错误
  AppException _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return const TimeoutException(message: '请求超时，请重试');

      case DioExceptionType.badResponse:
        return _handleResponseError(error.response);

      case DioExceptionType.cancel:
        return const AppException(message: '请求已取消');

      case DioExceptionType.connectionError:
        return const NetworkException(message: '网络连接失败，请检查网络设置');

      case DioExceptionType.badCertificate:
        return const AppException(message: 'SSL证书验证失败');

      case DioExceptionType.unknown:
      default:
        if (error.error != null) {
          return AppException(message: error.error.toString());
        }
        return const AppException(message: '未知错误');
    }
  }

  /// 处理响应错误
  AppException _handleResponseError(Response? response) {
    if (response == null) {
      return const ServerException(message: '服务器无响应');
    }

    final statusCode = response.statusCode ?? 0;
    final data = response.data;

    // 尝试从响应中提取错误消息
    String message = '请求失败';
    if (data is Map<String, dynamic>) {
      // Handle different types of error messages
      final detail = data['detail'];
      if (detail is String) {
        message = detail;
      } else if (detail is List) {
        // FastAPI validation errors return a list of error objects
        message = detail.map((e) {
          if (e is Map) {
            final msg = e['msg'] ?? e['message'] ?? '';
            final loc = e['loc'];
            if (loc is List && loc.length > 1) {
              return '${loc.last}: $msg';
            }
            return msg;
          }
          return e.toString();
        }).join(', ');
      } else {
        message = data['message']?.toString() ?? data['error']?.toString() ?? message;
      }
    }

    switch (statusCode) {
      case 400:
        return ServerException(
          message: message,
          statusCode: statusCode,
        );

      case 401:
        // Token过期或无效，清除本地Token
        SharedPreferences.getInstance().then((prefs) {
          prefs.remove(StorageKeys.accessToken);
          prefs.remove(StorageKeys.refreshToken);
        });
        return AuthenticationException(
          message: message,
          statusCode: statusCode,
        );

      case 403:
        return AuthorizationException(
          message: message,
          statusCode: statusCode,
        );

      case 404:
        return NotFoundException(
          message: message,
          statusCode: statusCode,
        );

      case 422:
        // 验证错误，提取详细错误信息
        Map<String, List<String>>? errors;
        if (data is Map<String, dynamic> && data.containsKey('errors')) {
          errors = (data['errors'] as Map<String, dynamic>).map(
            (key, value) => MapEntry(
              key,
              (value as List).map((e) => e.toString()).toList(),
            ),
          );
        }
        return ValidationException(
          message: message,
          statusCode: statusCode,
          errors: errors,
        );

      case 500:
      case 502:
      case 503:
      case 504:
        return ServerException(
          message: '服务器错误，请稍后重试',
          statusCode: statusCode,
        );

      default:
        return ServerException(
          message: message,
          statusCode: statusCode,
        );
    }
  }
}
