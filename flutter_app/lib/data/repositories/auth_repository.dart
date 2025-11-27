import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../core/errors/exceptions.dart';
import '../../core/storage/local_storage.dart';
import '../../core/constants/storage_keys.dart';
import '../../core/utils/logger.dart';
import '../datasources/remote/auth_api.dart';
import '../models/user_model.dart';

/// Authentication Repository
/// 认证仓库 - 处理认证相关的业务逻辑
class AuthRepository {
  final AuthApi _authApi;
  final LocalStorage _localStorage;

  AuthRepository({
    required AuthApi authApi,
    required LocalStorage localStorage,
  })  : _authApi = authApi,
        _localStorage = localStorage;

  /// Login
  /// 用户登录
  ///
  /// Returns:
  /// - Right(LoginResponse) on success
  /// - Left(Failure) on error
  Future<Either<Failure, LoginResponse>> login({
    required String username,
    required String password,
  }) async {
    try {
      AppLogger.info('AuthRepository.login: $username');

      final request = LoginRequest(
        username: username,
        password: password,
      );

      final response = await _authApi.login(request);

      // Save token to local storage
      await _localStorage.saveString(
        StorageKeys.accessToken,
        response.accessToken,
      );

      // Fetch user data separately since backend doesn't return it
      final userResult = await getCurrentUser();
      userResult.fold(
        (failure) {
          AppLogger.error('Failed to fetch user data after login: ${failure.message}');
          throw Exception('Failed to fetch user data: ${failure.message}');
        },
        (user) {
          AppLogger.debug('User data fetched and saved successfully');
        },
      );

      AppLogger.debug('Login successful, token saved');
      return Right(response);
    } on ServerException catch (e) {
      AppLogger.error('Login failed: ${e.message}');
      return Left(ServerFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on NetworkException catch (e) {
      AppLogger.error('Network error: ${e.message}');
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      AppLogger.error('Authentication failed: ${e.message}');
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on ValidationException catch (e) {
      AppLogger.error('Validation error: ${e.message}');
      return Left(ValidationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      AppLogger.error('Request timeout: ${e.message}');
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      AppLogger.error('Unknown error: $e');
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Register
  /// 用户注册
  ///
  /// Returns:
  /// - Right(LoginResponse) on success
  /// - Left(Failure) on error
  Future<Either<Failure, LoginResponse>> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      AppLogger.info('AuthRepository.register: $username, $email');

      final registerRequest = RegisterRequest(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );

      // Register the user (returns UserModel without tokens)
      await _authApi.register(registerRequest);
      AppLogger.debug('Registration successful, now logging in...');

      // Automatically login to get tokens
      final loginRequest = LoginRequest(
        username: username,
        password: password,
      );

      final loginResponse = await _authApi.login(loginRequest);

      // Save token to local storage
      await _localStorage.saveString(
        StorageKeys.accessToken,
        loginResponse.accessToken,
      );

      // Fetch user data separately since backend doesn't return it
      final userResult = await getCurrentUser();
      userResult.fold(
        (failure) {
          AppLogger.error('Failed to fetch user data after registration: ${failure.message}');
          throw Exception('Failed to fetch user data: ${failure.message}');
        },
        (user) {
          AppLogger.debug('User data fetched and saved successfully');
        },
      );

      AppLogger.debug('Auto-login successful, token saved');
      return Right(loginResponse);
    } on ServerException catch (e) {
      AppLogger.error('Registration failed: ${e.message}');
      return Left(ServerFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on NetworkException catch (e) {
      AppLogger.error('Network error: ${e.message}');
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      AppLogger.error('Validation error: ${e.message}');
      return Left(ValidationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      AppLogger.error('Request timeout: ${e.message}');
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      AppLogger.error('Unknown error: $e');
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get current user
  /// 获取当前登录用户信息
  ///
  /// Returns:
  /// - Right(UserModel) on success
  /// - Left(Failure) on error
  Future<Either<Failure, UserModel>> getCurrentUser() async {
    try {
      AppLogger.info('AuthRepository.getCurrentUser');

      final user = await _authApi.getCurrentUser();

      // Update local storage
      await _localStorage.saveInt(StorageKeys.userId, user.id);
      await _localStorage.saveString(StorageKeys.username, user.username);
      await _localStorage.saveString(StorageKeys.email, user.email);
      await _localStorage.saveString(StorageKeys.role, user.role);
      await _localStorage.saveBool(StorageKeys.isActive, user.isActive);

      AppLogger.debug('Get current user successful');
      return Right(user);
    } on ServerException catch (e) {
      AppLogger.error('Get user failed: ${e.message}');
      return Left(ServerFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on NetworkException catch (e) {
      AppLogger.error('Network error: ${e.message}');
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      AppLogger.error('Authentication failed: ${e.message}');
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      AppLogger.error('Request timeout: ${e.message}');
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      AppLogger.error('Unknown error: $e');
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Logout
  /// 用户登出
  ///
  /// Returns:
  /// - Right(true) on success
  /// - Left(Failure) on error
  Future<Either<Failure, bool>> logout() async {
    try {
      AppLogger.info('AuthRepository.logout');

      await _authApi.logout();

      // Clear all auth-related data from local storage
      await _clearAuthData();

      AppLogger.debug('Logout successful, auth data cleared');
      return const Right(true);
    } catch (e) {
      AppLogger.error('Logout error: $e');
      // Even if logout fails, clear local data
      await _clearAuthData();
      return Left(UnknownFailure(message: 'Logout error: $e'));
    }
  }

  /// Check if user is logged in
  /// 检查用户是否已登录
  ///
  /// Returns true if access token exists
  Future<bool> isLoggedIn() async {
    final token = await _localStorage.getString(StorageKeys.accessToken);
    return token != null && token.isNotEmpty;
  }

  /// Get cached user ID
  /// 获取缓存的用户ID
  Future<int?> getCachedUserId() async {
    return await _localStorage.getInt(StorageKeys.userId);
  }

  /// Get cached username
  /// 获取缓存的用户名
  Future<String?> getCachedUsername() async {
    return await _localStorage.getString(StorageKeys.username);
  }

  /// Get cached email
  /// 获取缓存的邮箱
  Future<String?> getCachedEmail() async {
    return await _localStorage.getString(StorageKeys.email);
  }

  /// Get cached user role
  /// 获取缓存的用户角色
  Future<String?> getCachedUserRole() async {
    return await _localStorage.getString(StorageKeys.role);
  }

  /// Change Password
  /// 修改密码
  ///
  /// Returns:
  /// - Right(true) on success
  /// - Left(Failure) on error
  Future<Either<Failure, bool>> changePassword({
    required String oldPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      AppLogger.info('AuthRepository.changePassword');

      final request = ChangePasswordRequest(
        oldPassword: oldPassword,
        newPassword: newPassword,
        confirmPassword: confirmPassword,
      );

      await _authApi.changePassword(request);

      AppLogger.debug('Password changed successfully');
      return const Right(true);
    } on ServerException catch (e) {
      AppLogger.error('Change password failed: ${e.message}');
      return Left(ServerFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on NetworkException catch (e) {
      AppLogger.error('Network error: ${e.message}');
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      AppLogger.error('Validation error: ${e.message}');
      return Left(ValidationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on AuthenticationException catch (e) {
      AppLogger.error('Authentication failed: ${e.message}');
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      AppLogger.error('Request timeout: ${e.message}');
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      AppLogger.error('Unknown error: $e');
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Clear authentication data from local storage
  Future<void> _clearAuthData() async {
    await _localStorage.remove(StorageKeys.accessToken);
    await _localStorage.remove(StorageKeys.userId);
    await _localStorage.remove(StorageKeys.username);
    await _localStorage.remove(StorageKeys.email);
    await _localStorage.remove(StorageKeys.role);
    await _localStorage.remove(StorageKeys.isActive);
  }
}
