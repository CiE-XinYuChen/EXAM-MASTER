import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/statistics_model.dart';

/// Statistics API
/// 统计数据相关API接口
class StatisticsApi {
  final DioClient _dioClient;

  StatisticsApi(this._dioClient);

  /// Get overall statistics
  /// 获取总体统计数据
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<StatisticsOverviewResponse> getOverview() async {
    try {
      AppLogger.info('StatisticsApi.getOverview');

      final response = await _dioClient.get(
        ApiConstants.statisticsOverview,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get statistics overview successful');
        return StatisticsOverviewResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get statistics overview',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get statistics overview error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get statistics by question bank
  /// 获取按题库分组的统计数据
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<BankStatisticsListResponse> getByBank() async {
    try {
      AppLogger.info('StatisticsApi.getByBank');

      final response = await _dioClient.get(
        ApiConstants.statisticsByBank,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get statistics by bank successful');
        return BankStatisticsListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get statistics by bank',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get statistics by bank error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get daily statistics
  /// 获取每日统计数据
  ///
  /// [days] - Number of days to retrieve (default: 7)
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<DailyStatisticsListResponse> getDaily({int days = 7}) async {
    try {
      AppLogger.info('StatisticsApi.getDaily: days=$days');

      final response = await _dioClient.get(
        ApiConstants.statisticsDaily,
        queryParameters: {'days': days},
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get daily statistics successful');
        return DailyStatisticsListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get daily statistics',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get daily statistics error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get statistics for a specific question bank
  /// 获取指定题库的统计数据
  ///
  /// [bankId] - Question bank ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<BankStatisticsResponse> getBankStatistics(String bankId) async {
    try {
      AppLogger.info('StatisticsApi.getBankStatistics: $bankId');

      final response = await _dioClient.get(
        ApiConstants.statisticsBankById(bankId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get bank statistics successful');
        return BankStatisticsResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get bank statistics',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get bank statistics error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Handle exceptions
  Exception _handleException(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return TimeoutException(message: 'Request timeout');
    }

    if (e.type == DioExceptionType.connectionError) {
      return NetworkException(message: 'Network connection error');
    }

    final statusCode = e.response?.statusCode;
    final message = e.response?.data?['message'] ?? e.message ?? 'Unknown error';

    if (statusCode != null) {
      switch (statusCode) {
        case 400:
          return ValidationException(message: message, statusCode: statusCode);
        case 401:
          return AuthenticationException(message: message, statusCode: statusCode);
        case 403:
          return AuthorizationException(message: message, statusCode: statusCode);
        case 404:
          return NotFoundException(message: message, statusCode: statusCode);
        case 422:
          final errors = e.response?.data?['errors'];
          return ValidationException(
            message: errors != null ? errors.toString() : message,
            statusCode: statusCode,
          );
        default:
          if (statusCode >= 500) {
            return ServerException(message: message, statusCode: statusCode);
          }
      }
    }

    return UnknownException(message: message);
  }
}
