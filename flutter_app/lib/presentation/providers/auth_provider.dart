import 'package:flutter/foundation.dart';
import '../../core/utils/logger.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/models/user_model.dart';
import '../../core/errors/failures.dart';

/// Authentication State
enum AuthState {
  initial,
  authenticated,
  unauthenticated,
  loading,
}

/// Authentication Provider
/// 认证状态管理
class AuthProvider with ChangeNotifier {
  final AuthRepository _authRepository;

  AuthProvider({required AuthRepository authRepository})
      : _authRepository = authRepository {
    _checkAuthStatus();
  }

  // State
  AuthState _state = AuthState.initial;
  UserModel? _currentUser;
  String? _errorMessage;

  // Getters
  AuthState get state => _state;
  UserModel? get currentUser => _currentUser;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _state == AuthState.authenticated;
  bool get isLoading => _state == AuthState.loading;

  /// Check authentication status on startup
  Future<void> _checkAuthStatus() async {
    try {
      final isLoggedIn = await _authRepository.isLoggedIn();

      if (isLoggedIn) {
        AppLogger.info('User is logged in, fetching user info');
        final result = await _authRepository.getCurrentUser();

        result.fold(
          (failure) {
            AppLogger.error('Failed to get user info: ${failure.message}');
            _state = AuthState.unauthenticated;
            notifyListeners();
          },
          (user) {
            AppLogger.info('User info loaded: ${user.username}');
            _currentUser = user;
            _state = AuthState.authenticated;
            notifyListeners();
          },
        );
      } else {
        AppLogger.info('User is not logged in');
        _state = AuthState.unauthenticated;
        notifyListeners();
      }
    } catch (e) {
      AppLogger.error('Error checking auth status: $e');
      _state = AuthState.unauthenticated;
      notifyListeners();
    }
  }

  /// Login
  Future<bool> login({
    required String username,
    required String password,
  }) async {
    _state = AuthState.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      AppLogger.info('AuthProvider.login: $username');

      final result = await _authRepository.login(
        username: username,
        password: password,
      );

      final loginSuccess = result.fold(
        (failure) {
          AppLogger.error('Login failed: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _state = AuthState.unauthenticated;
          notifyListeners();
          return false;
        },
        (response) {
          AppLogger.info('Login successful, token received');
          return true;
        },
      );

      if (loginSuccess) {
        // Fetch user info since repository already saved it to storage
        final userResult = await _authRepository.getCurrentUser();
        return userResult.fold(
          (failure) {
            AppLogger.error('Failed to get user info: ${failure.message}');
            _errorMessage = 'Login successful but failed to get user info';
            _state = AuthState.unauthenticated;
            notifyListeners();
            return false;
          },
          (user) {
            AppLogger.info('Login successful: ${user.username}');
            _currentUser = user;
            _state = AuthState.authenticated;
            _errorMessage = null;
            notifyListeners();
            return true;
          },
        );
      }

      return false;
    } catch (e) {
      AppLogger.error('Unexpected login error: $e');
      _errorMessage = '登录失败，请稍后重试';
      _state = AuthState.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// Register
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _state = AuthState.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      AppLogger.info('AuthProvider.register: $username, $email');

      final result = await _authRepository.register(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );

      final registerSuccess = result.fold(
        (failure) {
          AppLogger.error('Registration failed: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _state = AuthState.unauthenticated;
          notifyListeners();
          return false;
        },
        (response) {
          AppLogger.info('Registration successful, token received');
          return true;
        },
      );

      if (registerSuccess) {
        // Fetch user info since repository already saved it to storage
        final userResult = await _authRepository.getCurrentUser();
        return userResult.fold(
          (failure) {
            AppLogger.error('Failed to get user info: ${failure.message}');
            _errorMessage = 'Registration successful but failed to get user info';
            _state = AuthState.unauthenticated;
            notifyListeners();
            return false;
          },
          (user) {
            AppLogger.info('Registration successful: ${user.username}');
            _currentUser = user;
            _state = AuthState.authenticated;
            _errorMessage = null;
            notifyListeners();
            return true;
          },
        );
      }

      return false;
    } catch (e) {
      AppLogger.error('Unexpected registration error: $e');
      _errorMessage = '注册失败，请稍后重试';
      _state = AuthState.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      AppLogger.info('AuthProvider.logout');

      await _authRepository.logout();

      _currentUser = null;
      _state = AuthState.unauthenticated;
      _errorMessage = null;
      notifyListeners();

      AppLogger.info('Logout successful');
    } catch (e) {
      AppLogger.error('Logout error: $e');
      // Still clear state even if logout fails
      _currentUser = null;
      _state = AuthState.unauthenticated;
      notifyListeners();
    }
  }

  /// Refresh current user info
  Future<void> refreshUser() async {
    try {
      AppLogger.info('AuthProvider.refreshUser');

      final result = await _authRepository.getCurrentUser();

      result.fold(
        (failure) {
          AppLogger.error('Failed to refresh user: ${failure.message}');
          // Don't change state, just log error
        },
        (user) {
          AppLogger.info('User refreshed: ${user.username}');
          _currentUser = user;
          notifyListeners();
        },
      );
    } catch (e) {
      AppLogger.error('Error refreshing user: $e');
    }
  }

  /// Change Password
  Future<bool> changePassword({
    required String oldPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    _isLoading(true);
    _errorMessage = null;
    notifyListeners();

    try {
      AppLogger.info('AuthProvider.changePassword');

      final result = await _authRepository.changePassword(
        oldPassword: oldPassword,
        newPassword: newPassword,
        confirmPassword: confirmPassword,
      );

      return result.fold(
        (failure) {
          AppLogger.error('Change password failed: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _isLoading(false);
          notifyListeners();
          return false;
        },
        (success) {
          AppLogger.info('Password changed successfully');
          _isLoading(false);
          notifyListeners();
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error changing password: $e');
      _errorMessage = '修改密码失败，请稍后重试';
      _isLoading(false);
      notifyListeners();
      return false;
    }
  }

  void _isLoading(bool value) {
    if (value) {
      _state = AuthState.loading;
    } else {
      _state = AuthState.authenticated;
    }
  }

  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Convert Failure to user-friendly error message
  String _getErrorMessage(Failure failure) {
    if (failure is NetworkFailure) {
      return '网络连接失败，请检查网络设置';
    } else if (failure is AuthenticationFailure) {
      return '用户名或密码错误';
    } else if (failure is ValidationFailure) {
      return failure.message;
    } else if (failure is ServerFailure) {
      return '服务器错误，请稍后重试';
    } else if (failure is TimeoutFailure) {
      return '请求超时，请检查网络连接';
    } else {
      return '未知错误，请稍后重试';
    }
  }
}
