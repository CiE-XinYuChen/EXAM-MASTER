import 'package:dio/dio.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/utils/logger.dart';
import '../../models/question_bank_model.dart';
import '../../models/question_model.dart';
import '../../models/activation_model.dart';

/// Question Bank API
/// 题库相关API接口
class QuestionBankApi {
  final DioClient _dioClient;

  QuestionBankApi(this._dioClient);

  /// Get all question banks (public)
  /// 获取所有题库列表（公开）
  ///
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  /// [search] - Search keyword
  /// [category] - Category filter
  /// [isActive] - Active status filter
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  Future<QuestionBankListResponse> getQuestionBanks({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? category,
    bool? isActive,
  }) async {
    try {
      AppLogger.info('QuestionBankApi.getQuestionBanks: page=$page, pageSize=$pageSize');

      final queryParams = <String, dynamic>{
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      if (category != null && category.isNotEmpty) {
        queryParams['category'] = category;
      }
      if (isActive != null) {
        queryParams['is_active'] = isActive;
      }

      final response = await _dioClient.get(
        ApiConstants.questionBanks,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get question banks successful');

        // Backend returns List<QuestionBankModel> directly, not wrapped in object
        final List<dynamic> banksJson = response.data as List<dynamic>;
        final banks = banksJson.map((json) => QuestionBankModel.fromJson(json)).toList();

        // Create response with banks and total
        return QuestionBankListResponse(
          banks: banks,
          total: banks.length,
        );
      } else {
        throw ServerException(
          message: 'Failed to get question banks',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get question banks error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get question bank by ID
  /// 根据ID获取题库详情
  ///
  /// [bankId] - Question bank ID
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [NotFoundException]
  Future<QuestionBankModel> getQuestionBankById(String bankId) async {
    try {
      AppLogger.info('QuestionBankApi.getQuestionBankById: $bankId');

      final response = await _dioClient.get(
        ApiConstants.questionBankById(bankId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get question bank by ID successful');
        return QuestionBankModel.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get question bank',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get question bank error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get questions from a question bank
  /// 获取题库中的题目列表
  ///
  /// [bankId] - Question bank ID
  /// [page] - Page number (starts from 1)
  /// [pageSize] - Items per page
  /// [type] - Question type filter
  /// [difficulty] - Difficulty filter
  ///
  /// Requires authentication and active access to the question bank
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [AuthorizationException]
  Future<QuestionListResponse> getQuestions({
    required String bankId,
    int page = 1,
    int pageSize = 20,
    String? type,
    String? difficulty,
  }) async {
    try {
      AppLogger.info('QuestionBankApi.getQuestions: bankId=$bankId, page=$page');

      final queryParams = <String, dynamic>{
        'bank_id': bankId,
        'skip': (page - 1) * pageSize,
        'limit': pageSize,
      };

      if (type != null && type.isNotEmpty) {
        queryParams['type'] = type;
      }
      if (difficulty != null && difficulty.isNotEmpty) {
        queryParams['difficulty'] = difficulty;
      }

      final response = await _dioClient.get(
        ApiConstants.questionBankQuestions,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get questions successful');

        // Backend returns List<QuestionModel> directly, not wrapped in object
        final List<dynamic> questionsJson = response.data as List<dynamic>;
        final questions = questionsJson.map((json) => QuestionModel.fromJson(json)).toList();

        // Create response with questions and total
        return QuestionListResponse(
          questions: questions,
          total: questions.length,
        );
      } else {
        throw ServerException(
          message: 'Failed to get questions',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get questions error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get question by ID
  /// 根据ID获取题目详情
  ///
  /// [questionId] - Question ID
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [NotFoundException]
  Future<QuestionModel> getQuestionById(String questionId) async {
    try {
      AppLogger.info('QuestionBankApi.getQuestionById: $questionId');

      final response = await _dioClient.get(
        ApiConstants.questionById(questionId),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get question by ID successful');
        return QuestionModel.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get question',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get question error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Activate question bank with activation code
  /// 使用激活码激活题库
  ///
  /// [request] - Activation request with code
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  /// - [ValidationException]
  Future<ActivateCodeResponse> activateQuestionBank(
    ActivateCodeRequest request,
  ) async {
    try {
      AppLogger.info('QuestionBankApi.activateQuestionBank');

      final response = await _dioClient.post(
        ApiConstants.activateCode,
        data: request.toJson(),
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Activate question bank successful');
        return ActivateCodeResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to activate question bank',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Activate question bank error: ${e.message}');
      throw _handleException(e);
    } catch (e) {
      AppLogger.error('Unexpected error: $e');
      throw UnknownException(message: 'Unexpected error: $e');
    }
  }

  /// Get my activated question banks
  /// 获取我的已激活题库列表
  ///
  /// Requires authentication
  ///
  /// Throws:
  /// - [ServerException]
  /// - [NetworkException]
  /// - [AuthenticationException]
  Future<MyAccessListResponse> getMyAccess() async {
    try {
      AppLogger.info('QuestionBankApi.getMyAccess');

      final response = await _dioClient.get(
        ApiConstants.myAccess,
      );

      if (response.statusCode == 200) {
        AppLogger.debug('Get my access successful');
        return MyAccessListResponse.fromJson(response.data);
      } else {
        throw ServerException(
          message: 'Failed to get my access',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      AppLogger.error('Get my access error: ${e.message}');
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
