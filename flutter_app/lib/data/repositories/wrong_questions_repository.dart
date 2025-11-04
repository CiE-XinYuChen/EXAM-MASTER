import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../core/errors/exceptions.dart';
import '../datasources/remote/wrong_questions_api.dart';
import '../models/wrong_question_model.dart';

/// Wrong Questions Repository
class WrongQuestionsRepository {
  final WrongQuestionsApi _api;

  WrongQuestionsRepository({required WrongQuestionsApi api}) : _api = api;

  Future<Either<Failure, WrongQuestionListResponse>> getWrongQuestions({
    int page = 1,
    int pageSize = 20,
    String? bankId,
    bool? corrected,
  }) async {
    try {
      final result = await _api.getWrongQuestions(
        page: page,
        pageSize: pageSize,
        bankId: bankId,
        corrected: corrected,
      );
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

  Future<Either<Failure, WrongQuestionModel>> markAsCorrected(
    String wrongQuestionId,
    bool corrected,
  ) async {
    try {
      final result = await _api.markCorrected(wrongQuestionId, corrected);
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

  Future<Either<Failure, WrongQuestionAnalysisModel>> getAnalysis({String? bankId}) async {
    try {
      final result = await _api.getAnalysis(bankId: bankId);
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

  Future<Either<Failure, void>> deleteWrongQuestion(String wrongQuestionId) async {
    try {
      await _api.deleteWrongQuestion(wrongQuestionId);
      return const Right(null);
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
