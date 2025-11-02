import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../core/errors/exceptions.dart';
import '../datasources/remote/favorites_api.dart';
import '../models/favorite_model.dart';

/// Favorites Repository
class FavoritesRepository {
  final FavoritesApi _api;

  FavoritesRepository({required FavoritesApi api}) : _api = api;

  Future<Either<Failure, FavoriteListResponse>> getFavorites({
    int page = 1,
    int pageSize = 20,
    String? bankId,
  }) async {
    try {
      final result = await _api.getFavorites(page: page, pageSize: pageSize, bankId: bankId);
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

  Future<Either<Failure, AddFavoriteResponse>> addFavorite(AddFavoriteRequest request) async {
    try {
      final result = await _api.addFavorite(request);
      return Right(result);
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

  Future<Either<Failure, void>> removeFavorite(String favoriteId) async {
    try {
      await _api.removeFavorite(favoriteId);
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

  Future<Either<Failure, void>> updateNote(String favoriteId, UpdateFavoriteNoteRequest request) async {
    try {
      await _api.updateNote(favoriteId, request);
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

  Future<Either<Failure, bool>> isFavorited(String questionId) async {
    try {
      final result = await _api.isFavorited(questionId);
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
