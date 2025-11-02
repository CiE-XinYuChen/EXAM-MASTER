import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../core/errors/exceptions.dart';
import '../../core/utils/logger.dart';
import '../datasources/remote/practice_api.dart';
import '../models/practice_session_model.dart';
import '../models/answer_record_model.dart';

/// Practice Repository
/// 答题练习仓库
class PracticeRepository {
  final PracticeApi _api;

  PracticeRepository({required PracticeApi api}) : _api = api;

  /// Create a new practice session
  Future<Either<Failure, CreatePracticeSessionResponse>> createSession(
    CreatePracticeSessionRequest request,
  ) async {
    try {
      final response = await _api.createSession(request);
      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AuthenticationException catch (e) {
      return Left(AuthenticationFailure(message: e.message, statusCode: e.statusCode));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message, statusCode: e.statusCode));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Get practice session by ID
  Future<Either<Failure, PracticeSessionModel>> getSession(String sessionId) async {
    try {
      final session = await _api.getSession(sessionId);
      return Right(session);
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

  /// Get user's practice sessions
  Future<Either<Failure, List<PracticeSessionModel>>> getMySessions({
    int page = 1,
    int pageSize = 20,
    String? bankId,
    String? status,
  }) async {
    try {
      final sessions = await _api.getMySessions(
        page: page,
        pageSize: pageSize,
        bankId: bankId,
        status: status,
      );
      return Right(sessions);
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

  /// Submit answer for a question
  Future<Either<Failure, SubmitAnswerResponse>> submitAnswer(
    String sessionId,
    SubmitAnswerRequest request,
  ) async {
    try {
      final response = await _api.submitAnswer(sessionId, request);
      return Right(response);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message, statusCode: e.statusCode));
    } on TimeoutException catch (e) {
      return Left(TimeoutFailure(message: e.message));
    } catch (e) {
      return Left(UnknownFailure(message: 'Unexpected error: $e'));
    }
  }

  /// Complete a practice session
  Future<Either<Failure, Map<String, dynamic>>> completeSession(String sessionId) async {
    try {
      final result = await _api.completeSession(sessionId);
      return Right(result);
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

  /// Get answer history for a session
  Future<Either<Failure, AnswerHistoryResponse>> getAnswerHistory(String sessionId) async {
    try {
      final history = await _api.getAnswerHistory(sessionId);
      return Right(history);
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

  /// Pause a practice session
  Future<Either<Failure, Map<String, dynamic>>> pauseSession(String sessionId) async {
    try {
      final result = await _api.pauseSession(sessionId);
      return Right(result);
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

  /// Resume a practice session
  Future<Either<Failure, Map<String, dynamic>>> resumeSession(String sessionId) async {
    try {
      final result = await _api.resumeSession(sessionId);
      return Right(result);
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
}
