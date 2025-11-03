import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/user_model.dart';

/// Authentication API
/// 认证相关API接口
class AuthApi {
  final DioClient _dioClient;

  AuthApi(this._dioClient);

  /// Login
  /// 用户登录
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [ValidationException]
  Future<LoginResponse> login(LoginRequest request) async {
    try {
      AppLogger.info('AuthApi.login: ${request.username}');

      // Backend expects form data (OAuth2PasswordRequestForm), not JSON
      final response = await _dioClient.post(
        ApiConstants.login,
        data: FormData.fromMap({
          'username': request.username,
          'password': request.password,
        }),
        options: Options(
          contentType: Headers.formUrlEncodedContentType,
        ),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Login successful');
        return LoginResponse.fromJson(response.data);
      } else {
        AppLogger.error('Login failed: ${response.statusCode}');
        throw ServerException(
          message: 'Login failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Login error: ${e.message}');
      throw _handleDioException(e);
    } catch (e) {
      AppLogger.error('Unexpected login error: $e');
      throw UnknownException(message: 'Unexpected error during login: $e');
    }
  }

  /// Register
  /// 用户注册
  ///
  /// Returns the created user (without tokens)
  /// Caller should login separately to get tokens
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [ValidationException]
  Future<UserModel> register(RegisterRequest request) async {
    try {
      AppLogger.info('AuthApi.register: ${request.username}');
      AppLogger.debug('Register request data: ${request.toJson()}');

      final response = await _dioClient.post(
        ApiConstants.register,
        data: request.toJson(),
      );

      AppLogger.debug('Register response status: ${response.statusCode}');
      AppLogger.debug('Register response data: ${response.data}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.debug('Registration successful');
        return UserModel.fromJson(response.data);
      } else {
        AppLogger.error('Registration failed: ${response.statusCode}');
        throw ServerException(
          message: 'Registration failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Registration DioException type: ${e.type}');
      AppLogger.error('Registration DioException message: ${e.message}');
      AppLogger.error('Registration DioException response: ${e.response?.data}');
      AppLogger.error('Registration DioException status: ${e.response?.statusCode}');
      throw _handleDioException(e);
    } catch (e, stackTrace) {
      AppLogger.error('Unexpected registration error: $e');
      AppLogger.error('Stack trace: $stackTrace');
      throw UnknownException(message: 'Unexpected error during registration: $e');
    }
  }

  /// Get current user info
  /// 获取当前用户信息
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<UserModel> getCurrentUser() async {
    try {
      AppLogger.info('AuthApi.getCurrentUser');

      final response = await _dioClient.get(ApiConstants.currentUser);

      if (response.statusCode == 200) {
        AppLogger.debug('Get current user successful');
        return UserModel.fromJson(response.data);
      } else {
        AppLogger.error('Get current user failed: ${response.statusCode}');
        throw ServerException(
          message: 'Failed to get user info',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get current user error: ${e.message}');
      throw _handleDioException(e);
    } catch (e) {
      AppLogger.error('Unexpected get user error: $e');
      throw UnknownException(message: 'Unexpected error getting user: $e');
    }
  }

  /// Logout
  /// 用户登出
  ///
  /// This is a client-side operation that clears the token
  Future<void> logout() async {
    try {
      AppLogger.info('AuthApi.logout');
      // Clear token from DioClient
      _dioClient.clearToken();
      AppLogger.debug('Logout successful');
    } catch (e) {
      AppLogger.error('Logout error: $e');
      throw UnknownException(message: 'Unexpected error during logout: $e');
    }
  }

  /// Handle Dio exceptions and convert to app exceptions
  Exception _handleDioException(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return TimeoutException(message: 'Request timeout');
    }

    if (e.type == DioExceptionType.connectionError) {
      return NetworkException(message: 'Network connection error');
    }

    final statusCode = e.response?.statusCode;
    // Try to extract error message from response (FastAPI uses 'detail')
    String message = 'Unknown error';
    if (e.response?.data != null) {
      final data = e.response!.data;
      if (data is Map) {
        message = data['detail']?.toString() ??
                  data['message']?.toString() ??
                  e.message ??
                  'Unknown error';
      }
    }

    if (statusCode != null) {
      switch (statusCode) {
        case 400:
          return ValidationException(
            message: message,
            statusCode: statusCode,
          );
        case 401:
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
          // Extract validation errors from response
          final errors = e.response?.data?['errors'];
          return ValidationException(
            message: errors != null ? errors.toString() : message,
            statusCode: statusCode,
          );
        default:
          if (statusCode >= 500) {
            return ServerException(
              message: message,
              statusCode: statusCode,
            );
          }
      }
    }

    return UnknownException(message: message);
  }
}
