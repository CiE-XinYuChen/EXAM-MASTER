import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../core/errors/exceptions.dart';
import '../../core/utils/logger.dart';
import '../datasources/remote/question_bank_api.dart';
import '../models/question_bank_model.dart';
import '../models/question_model.dart';
import '../models/activation_model.dart';

/// Question Bank Repository
/// 题库仓库 - 处理题库相关的业务逻辑
class QuestionBankRepository {
  final QuestionBankApi _api;

  QuestionBankRepository({required QuestionBankApi api}) : _api = api;

  /// Get all question banks
  /// 获取所有题库列表
  Future<Either<Failure, QuestionBankListResponse>> getQuestionBanks({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? category,
    bool? isActive,
  }) async {
    try {
      AppLogger.info('QuestionBankRepository.getQuestionBanks: page=$page');

      final response = await _api.getQuestionBanks(
        page: page,
        pageSize: pageSize,
        search: search,
        category: category,
        isActive: isActive,
      );

      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get question bank by ID
  /// 根据ID获取题库详情
  Future<Either<Failure, QuestionBankModel>> getQuestionBankById(
    String bankId,
  ) async {
    try {
      AppLogger.info('QuestionBankRepository.getQuestionBankById: $bankId');

      final bank = await _api.getQuestionBankById(bankId);

      return Right(bank);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message, statusCode: e.statusCode));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get questions from a question bank
  /// 获取题库中的题目列表
  Future<Either<Failure, QuestionListResponse>> getQuestions({
    required String bankId,
    int page = 1,
    int pageSize = 20,
    String? type,
    String? difficulty,
  }) async {
    try {
      AppLogger.info('QuestionBankRepository.getQuestions: bankId=$bankId');

      final response = await _api.getQuestions(
        bankId: bankId,
        page: page,
        pageSize: pageSize,
        type: type,
        difficulty: difficulty,
      );

      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on AuthorizationException catch (e) {
      return Left(AuthorizationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get question by ID
  /// 根据ID获取题目详情
  Future<Either<Failure, QuestionModel>> getQuestionById(
    String questionId,
  ) async {
    try {
      AppLogger.info('QuestionBankRepository.getQuestionById: $questionId');

      final question = await _api.getQuestionById(questionId);

      return Right(question);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message, statusCode: e.statusCode));
    } on AuthenticationException catch (e) {
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Activate question bank with activation code
  /// 使用激活码激活题库
  Future<Either<Failure, ActivateCodeResponse>> activateQuestionBank(
    String code,
  ) async {
    try {
      AppLogger.info('QuestionBankRepository.activateQuestionBank');

      final request = ActivateCodeRequest(code: code);
      final response = await _api.activateQuestionBank(request);

      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get my activated question banks
  /// 获取我的已激活题库列表
  Future<Either<Failure, MyAccessListResponse>> getMyAccess() async {
    try {
      AppLogger.info('QuestionBankRepository.getMyAccess');

      final response = await _api.getMyAccess();

      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      return Left(AuthenticationFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }
}
