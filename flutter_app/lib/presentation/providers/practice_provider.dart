import 'package:flutter/foundation.dart';
import '../../core/utils/logger.dart';
import '../../data/repositories/practice_repository.dart';
import '../../data/repositories/question_bank_repository.dart';
import '../../data/models/practice_session_model.dart';
import '../../data/models/question_model.dart';
import '../../data/models/answer_record_model.dart';
import '../../core/errors/failures.dart';

/// Practice Provider
/// 答题练习状态管理
class PracticeProvider with ChangeNotifier {
  final PracticeRepository _repository;
  final QuestionBankRepository _questionBankRepository;
  final int? Function() _getUserId;

  PracticeProvider({
    required PracticeRepository repository,
    required QuestionBankRepository questionBankRepository,
    required int? Function() getUserId,
  })  : _repository = repository,
        _questionBankRepository = questionBankRepository,
        _getUserId = getUserId;

  // State
  bool _isLoading = false;
  String? _errorMessage;
  PracticeSessionModel? _currentSession;
  List<QuestionModel> _questions = [];
  int _currentQuestionIndex = 0;
  Map<String, dynamic> _userAnswers = {}; // questionId -> answer
  Map<String, SubmitAnswerResponse> _answerResults = {}; // questionId -> result

  // Getters
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  PracticeSessionModel? get currentSession => _currentSession;
  List<QuestionModel> get questions => _questions;
  int get currentQuestionIndex => _currentQuestionIndex;
  Map<String, dynamic> get userAnswers => _userAnswers;
  Map<String, SubmitAnswerResponse> get answerResults => _answerResults;

  QuestionModel? get currentQuestion {
    if (_currentQuestionIndex >= 0 && _currentQuestionIndex < _questions.length) {
      return _questions[_currentQuestionIndex];
    }
    return null;
  }

  bool get hasNextQuestion => _currentQuestionIndex < _questions.length - 1;
  bool get hasPreviousQuestion => _currentQuestionIndex > 0;
  bool get isLastQuestion => _currentQuestionIndex == _questions.length - 1;
  bool get isFirstQuestion => _currentQuestionIndex == 0;

  int get totalQuestions => _questions.length;
  int get answeredCount => _userAnswers.length;
  double get progress => totalQuestions > 0 ? answeredCount / totalQuestions : 0.0;

  /// Create a new practice session
  Future<bool> createSession({
    required String bankId,
    required PracticeMode mode,
    List<String>? questionTypes,
    String? difficulty,
  }) async {
    _setLoading(true);

    try {
      AppLogger.info('PracticeProvider.createSession: bankId=$bankId, mode=$mode');

      // Convert PracticeMode enum to string
      String modeString;
      switch (mode) {
        case PracticeMode.sequential:
          modeString = 'sequential';
          break;
        case PracticeMode.random:
          modeString = 'random';
          break;
        case PracticeMode.wrongOnly:
          modeString = 'wrong_only';
          break;
        case PracticeMode.favoriteOnly:
          modeString = 'favorite_only';
          break;
        case PracticeMode.unpracticed:
          modeString = 'unpracticed';
          break;
      }

      final request = CreatePracticeSessionRequest(
        bankId: bankId,
        mode: modeString,
        questionTypes: questionTypes,
        difficulty: difficulty,
      );

      final createResult = await _repository.createSession(request);

      return await createResult.fold(
        (failure) {
          AppLogger.error('Failed to create session: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
          return false;
        },
        (response) async {
          AppLogger.info('Session created: ${response.sessionId}');

          // Get the session details
          final sessionResult = await _repository.getSession(response.sessionId);

          return await sessionResult.fold(
            (failure) {
              AppLogger.error('Failed to get session: ${failure.message}');
              _errorMessage = _getErrorMessage(failure);
              _setLoading(false);
              return false;
            },
            (session) async {
              _currentSession = session;

              // Get questions from the bank
              // Use session's total questions count, or a large number if not specified
              final pageSize = session.totalQuestions ?? 10000;
              final questionsResult = await _questionBankRepository.getQuestions(
                bankId: bankId,
                page: 1,
                pageSize: pageSize,
              );

              return questionsResult.fold(
                (failure) {
                  AppLogger.error('Failed to get questions: ${failure.message}');
                  _errorMessage = _getErrorMessage(failure);
                  _setLoading(false);
                  return false;
                },
                (questionResponse) {
                  AppLogger.info('Questions loaded: ${questionResponse.questions.length}');

                  // If session has specific question IDs, filter the questions
                  if (session.questionIds != null && session.questionIds!.isNotEmpty) {
                    _questions = questionResponse.questions
                        .where((q) => session.questionIds!.contains(q.id))
                        .toList();
                  } else {
                    _questions = questionResponse.questions;
                  }

                  // Apply mode-specific filtering or shuffling
                  if (mode == PracticeMode.random && _questions.isNotEmpty) {
                    _questions.shuffle();
                  }

                  _currentQuestionIndex = session.currentIndex;
                  _userAnswers = {};
                  _errorMessage = null;
                  _setLoading(false);
                  return true;
                },
              );
            },
          );
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error creating session: $e');
      _errorMessage = '创建答题会话失败，请稍后重试';
      _setLoading(false);
      return false;
    }
  }

  /// Get practice session by ID
  Future<void> getSession(String sessionId) async {
    _setLoading(true);

    try {
      AppLogger.info('PracticeProvider.getSession: $sessionId');

      final result = await _repository.getSession(sessionId);

      result.fold(
        (failure) {
          AppLogger.error('Failed to get session: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
        },
        (session) {
          AppLogger.info('Session loaded: ${session.id}');
          _currentSession = session;
          _errorMessage = null;
          _setLoading(false);
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error getting session: $e');
      _errorMessage = '获取答题会话失败，请稍后重试';
      _setLoading(false);
    }
  }

  /// Submit an answer
  Future<bool> submitAnswer({
    required String questionId,
    required dynamic userAnswer,
  }) async {
    try {
      if (_currentSession == null) {
        _errorMessage = '未找到答题会话';
        return false;
      }

      final userId = _getUserId();
      if (userId == null) {
        _errorMessage = '未找到用户信息';
        return false;
      }

      AppLogger.info('PracticeProvider.submitAnswer: questionId=$questionId');

      // Convert userAnswer to Map<String, dynamic> format
      Map<String, dynamic> answerMap;
      if (userAnswer is String) {
        // For single choice, judge, essay
        answerMap = {'answer': userAnswer};
      } else if (userAnswer is List) {
        if (userAnswer.isEmpty) {
          answerMap = {'answers': []};
        } else if (userAnswer.first is String && userAnswer.length == 1 && userAnswer.first.length < 10) {
          // Might be multiple choice answers like ['A', 'B']
          answerMap = {'answers': userAnswer};
        } else {
          // Fill in the blank answers
          answerMap = {'fill_answers': userAnswer};
        }
      } else if (userAnswer is bool) {
        // For judge questions
        answerMap = {'answer': userAnswer.toString()};
      } else if (userAnswer is Map) {
        answerMap = Map<String, dynamic>.from(userAnswer);
      } else {
        answerMap = {'answer': userAnswer.toString()};
      }

      final request = SubmitAnswerRequest(
        userId: userId,
        questionId: questionId,
        sessionId: _currentSession!.id,
        userAnswer: answerMap,
      );

      final result = await _repository.submitAnswer(
        _currentSession!.id,
        request,
      );

      return result.fold(
        (failure) {
          AppLogger.error('Failed to submit answer: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          notifyListeners();
          return false;
        },
        (response) {
          AppLogger.info('Answer submitted: ${response.isCorrect ? "Correct" : "Incorrect"}');

          // Update local answer
          _userAnswers[questionId] = userAnswer;

          // Store the answer result for UI display
          _answerResults[questionId] = response;

          _errorMessage = null;
          notifyListeners();
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error submitting answer: $e');
      _errorMessage = '提交答案失败，请稍后重试';
      notifyListeners();
      return false;
    }
  }

  /// Set answer locally (without submitting)
  void setAnswer(String questionId, dynamic answer) {
    _userAnswers[questionId] = answer;
    notifyListeners();
  }

  /// Get answer for a question
  dynamic getAnswer(String questionId) {
    return _userAnswers[questionId];
  }

  /// Get answer result for a question (includes options with correctness)
  SubmitAnswerResponse? getAnswerResult(String questionId) {
    return _answerResults[questionId];
  }

  /// Clear answer for a question
  void clearAnswer(String questionId) {
    _userAnswers.remove(questionId);
    notifyListeners();
  }

  /// Go to next question
  void nextQuestion() {
    if (hasNextQuestion) {
      _currentQuestionIndex++;
      notifyListeners();
    }
  }

  /// Go to previous question
  void previousQuestion() {
    if (hasPreviousQuestion) {
      _currentQuestionIndex--;
      notifyListeners();
    }
  }

  /// Go to specific question
  void goToQuestion(int index) {
    if (index >= 0 && index < _questions.length) {
      _currentQuestionIndex = index;
      notifyListeners();
    }
  }

  /// Complete session
  Future<bool> completeSession() async {
    if (_currentSession == null) {
      _errorMessage = '未找到答题会话';
      return false;
    }

    _setLoading(true);

    try {
      AppLogger.info('PracticeProvider.completeSession: ${_currentSession!.id}');

      final result = await _repository.completeSession(
        _currentSession!.id,
      );

      return result.fold(
        (failure) {
          AppLogger.error('Failed to complete session: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          _setLoading(false);
          return false;
        },
        (response) {
          AppLogger.info('Session completed');
          // Response is Map<String, dynamic>, not session model
          _errorMessage = null;
          _setLoading(false);
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error completing session: $e');
      _errorMessage = '完成答题会话失败，请稍后重试';
      _setLoading(false);
      return false;
    }
  }

  /// Pause session
  Future<bool> pauseSession() async {
    if (_currentSession == null) {
      _errorMessage = '未找到答题会话';
      return false;
    }

    try {
      AppLogger.info('PracticeProvider.pauseSession: ${_currentSession!.id}');

      final result = await _repository.pauseSession(
        _currentSession!.id,
      );

      return result.fold(
        (failure) {
          AppLogger.error('Failed to pause session: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          notifyListeners();
          return false;
        },
        (response) {
          AppLogger.info('Session paused');
          // Response is Map<String, dynamic>
          _errorMessage = null;
          notifyListeners();
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error pausing session: $e');
      _errorMessage = '暂停答题会话失败，请稍后重试';
      notifyListeners();
      return false;
    }
  }

  /// Resume session
  Future<bool> resumeSession() async {
    if (_currentSession == null) {
      _errorMessage = '未找到答题会话';
      return false;
    }

    try {
      AppLogger.info('PracticeProvider.resumeSession: ${_currentSession!.id}');

      final result = await _repository.resumeSession(
        _currentSession!.id,
      );

      return result.fold(
        (failure) {
          AppLogger.error('Failed to resume session: ${failure.message}');
          _errorMessage = _getErrorMessage(failure);
          notifyListeners();
          return false;
        },
        (response) {
          AppLogger.info('Session resumed');
          // Response is Map<String, dynamic>
          _errorMessage = null;
          notifyListeners();
          return true;
        },
      );
    } catch (e) {
      AppLogger.error('Unexpected error resuming session: $e');
      _errorMessage = '恢复答题会话失败，请稍后重试';
      notifyListeners();
      return false;
    }
  }

  /// Clear current session
  void clearSession() {
    _currentSession = null;
    _questions = [];
    _currentQuestionIndex = 0;
    _userAnswers = {};
    _answerResults = {};
    _errorMessage = null;
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
      return '题目或会话不存在';
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
