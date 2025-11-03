import 'package:flutter/foundation.dart';
import '../../core/utils/logger.dart';
import '../../data/repositories/question_bank_repository.dart';
import '../../data/models/question_bank_model.dart';
import '../../data/models/question_model.dart';
import '../../data/models/activation_model.dart';
import '../../core/errors/failures.dart';

/// Question Bank Provider
/// 题库状态管理
class QuestionBankProvider with ChangeNotifier {
  final QuestionBankRepository _repository;

  QuestionBankProvider({required QuestionBankRepository repository})
      : _repository = repository;

  // State
  bool _isLoading = false;
  String? _errorMessage;
  List<QuestionBankModel> _questionBanks = [];
  QuestionBankModel? _currentQuestionBank;
  List<QuestionModel> _questions = [];
  List<ActivationAccessModel> _myAccess = [];

  // Getters
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<QuestionBankModel> get questionBanks => _questionBanks;
  QuestionBankModel? get currentQuestionBank => _currentQuestionBank;
  List<QuestionModel> get questions => _questions;
  List<ActivationAccessModel> get myAccess => _myAccess;

  /// Get all question banks
  Future<void> getQuestionBanks({
    int page = 1,
    int pageSize = 20,
    String? search,
  }) async {
    _setLoading(true);

    try {
      AppLogger.info('QuestionBankProvider.getQuestionBanks: page=$page');

      final result = await _repository.getQuestionBanks(
        page: page,
        pageSize: pageSize,
        search: search,
      );

      result.fold(
        (failure) {
          AppLogger.error('Failed to get question banks: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
        },
        (response) {
          AppLogger.info('Question banks loaded: ${response.banks.length} banks');
          _questionBanks = response.banks;
          _errorMessage = null;
          _setLoading(false);
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error getting question banks: $e');
      _errorMessage = '获取题库列表失败，请稍后重试';
      _setLoading(false);
    }
  }

  /// Get question bank by ID
  Future<void> getQuestionBankById(String bankId) async {
    _setLoading(true);

    try {
      AppLogger.info('QuestionBankProvider.getQuestionBankById: $bankId');

      final result = await _repository.getQuestionBankById(bankId);

      result.fold(
        (failure) {
          AppLogger.error('Failed to get question bank: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
        },
        (questionBank) {
          AppLogger.info('Question bank loaded: ${questionBank.name}');
          _currentQuestionBank = questionBank;
          _errorMessage = null;
          _setLoading(false);
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error getting question bank: $e');
      _errorMessage = '获取题库详情失败，请稍后重试';
      _setLoading(false);
    }
  }

  /// Get questions from a question bank
  Future<void> getQuestions({
    required String bankId,
    int page = 1,
    int pageSize = 20,
    String? questionType,
    String? difficulty,
  }) async {
    _setLoading(true);

    try {
      AppLogger.info('QuestionBankProvider.getQuestions: bankId=$bankId');

      final result = await _repository.getQuestions(
        bankId: bankId,
        page: page,
        pageSize: pageSize,
        type: questionType,
        difficulty: difficulty,
      );

      result.fold(
        (failure) {
          AppLogger.error('Failed to get questions: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
        },
        (response) {
          AppLogger.info('Questions loaded: ${response.questions.length} questions');
          _questions = response.questions;
          _errorMessage = null;
          _setLoading(false);
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error getting questions: $e');
      _errorMessage = '获取题目列表失败，请稍后重试';
      _setLoading(false);
    }
  }

  /// Activate question bank with code
  Future<bool> activateCode(String activationCode) async {
    _setLoading(true);

    try {
      AppLogger.info('QuestionBankProvider.activateCode');

      final result = await _repository.activateQuestionBank(activationCode);

      return result.fold(
        (failure) {
          AppLogger.error('Failed to activate code: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
          return false;
        },
        (response) {
          AppLogger.info('Code activated successfully: ${response.message}');
          _errorMessage = null;
          _setLoading(false);
          // Refresh question banks list
          getQuestionBanks();
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error activating code: $e');
      _errorMessage = '激活失败，请稍后重试';
      _setLoading(false);
      return false;
    }
  }

  /// Get my activated question banks
  Future<void> getMyAccess() async {
    _setLoading(true);

    try {
      AppLogger.info('QuestionBankProvider.getMyAccess');

      final result = await _repository.getMyAccess();

      result.fold(
        (failure) {
          AppLogger.error('Failed to get my access: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
        },
        (response) {
          AppLogger.info('My access loaded: ${response.access.length} items');
          _myAccess = response.access;
          _errorMessage = null;
          _setLoading(false);
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error getting my access: $e');
      _errorMessage = '获取我的权限失败，请稍后重试';
      _setLoading(false);
    }
  }

  /// Clear current question bank
  void clearCurrentQuestionBank() {
    _currentQuestionBank = null;
    notifyListeners();
  }

  /// Clear questions
  void clearQuestions() {
    _questions = [];
    notifyListeners();
  }

  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Set loading state
  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  /// Convert Failure to user-friendly error message
  String _getErrorMessage(Failure failure) {
    if (failure is NetworkFailure) {
      return '网络连接失败，请检查网络设置';
    } else if (failure is AuthenticationFailure) {
      return '请先登录';
    } else if (failure is AuthorizationFailure) {
      return '没有权限访问该题库，请先激活';
    } else if (failure is NotFoundFailure) {
      return '题库不存在';
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
