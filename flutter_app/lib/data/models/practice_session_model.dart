import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'practice_session_model.g.dart';

/// Practice Mode Enum
enum PracticeMode {
  @JsonValue('sequential')
  sequential,
  @JsonValue('random')
  random,
  @JsonValue('wrong_only')
  wrongOnly,
  @JsonValue('favorite_only')
  favoriteOnly,
  @JsonValue('unpracticed')
  unpracticed,
}

/// Session Status Enum
enum SessionStatus {
  @JsonValue('in_progress')
  inProgress,
  @JsonValue('completed')
  completed,
  @JsonValue('paused')
  paused,
}

/// Practice Session Model
/// 答题会话数据模型
@JsonSerializable()
class PracticeSessionModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  final PracticeMode mode;
  @JsonKey(name: 'total_questions')
  final int totalQuestions;
  @JsonKey(name: 'current_index')
  final int currentIndex;
  @JsonKey(name: 'completed_count')
  final int completedCount;
  @JsonKey(name: 'correct_count')
  final int correctCount;
  final SessionStatus status;
  @JsonKey(name: 'question_ids')
  final List<String>? questionIds;
  @JsonKey(name: 'started_at')
  final String startedAt;
  @JsonKey(name: 'completed_at')
  final String? completedAt;
  @JsonKey(name: 'last_activity_at')
  final String? lastActivityAt;

  const PracticeSessionModel({
    required this.id,
    required this.userId,
    required this.bankId,
    required this.mode,
    required this.totalQuestions,
    required this.currentIndex,
    required this.completedCount,
    required this.correctCount,
    required this.status,
    this.questionIds,
    required this.startedAt,
    this.completedAt,
    this.lastActivityAt,
  });

  factory PracticeSessionModel.fromJson(Map<String, dynamic> json) =>
      _$PracticeSessionModelFromJson(json);

  Map<String, dynamic> toJson() => _$PracticeSessionModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        bankId,
        mode,
        totalQuestions,
        currentIndex,
        completedCount,
        correctCount,
        status,
        questionIds,
        startedAt,
        completedAt,
        lastActivityAt,
      ];

  PracticeSessionModel copyWith({
    String? id,
    int? userId,
    String? bankId,
    PracticeMode? mode,
    int? totalQuestions,
    int? currentIndex,
    int? completedCount,
    int? correctCount,
    SessionStatus? status,
    List<String>? questionIds,
    String? startedAt,
    String? completedAt,
    String? lastActivityAt,
  }) {
    return PracticeSessionModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      bankId: bankId ?? this.bankId,
      mode: mode ?? this.mode,
      totalQuestions: totalQuestions ?? this.totalQuestions,
      currentIndex: currentIndex ?? this.currentIndex,
      completedCount: completedCount ?? this.completedCount,
      correctCount: correctCount ?? this.correctCount,
      status: status ?? this.status,
      questionIds: questionIds ?? this.questionIds,
      startedAt: startedAt ?? this.startedAt,
      completedAt: completedAt ?? this.completedAt,
      lastActivityAt: lastActivityAt ?? this.lastActivityAt,
    );
  }

  /// Calculate accuracy rate
  double get accuracyRate {
    if (completedCount == 0) return 0.0;
    return (correctCount / completedCount) * 100;
  }

  /// Calculate progress percentage
  double get progressPercentage {
    if (totalQuestions == 0) return 0.0;
    return (completedCount / totalQuestions) * 100;
  }

  /// Check if session is completed
  bool get isCompleted => status == SessionStatus.completed;

  /// Check if session can be resumed
  bool get canResume =>
      status == SessionStatus.inProgress || status == SessionStatus.paused;
}

/// Create Practice Session Request
@JsonSerializable()
class CreatePracticeSessionRequest {
  @JsonKey(name: 'bank_id')
  final String bankId;
  final String mode;
  @JsonKey(name: 'question_types')
  final List<String>? questionTypes;
  final String? difficulty;

  const CreatePracticeSessionRequest({
    required this.bankId,
    required this.mode,
    this.questionTypes,
    this.difficulty,
  });

  Map<String, dynamic> toJson() => _$CreatePracticeSessionRequestToJson(this);
}

/// Create Practice Session Response
@JsonSerializable()
class CreatePracticeSessionResponse extends Equatable {
  final bool success;
  @JsonKey(name: 'session_id')
  final String sessionId;
  @JsonKey(name: 'total_questions')
  final int totalQuestions;
  final String mode;
  final String? message;

  const CreatePracticeSessionResponse({
    required this.success,
    required this.sessionId,
    required this.totalQuestions,
    required this.mode,
    this.message,
  });

  factory CreatePracticeSessionResponse.fromJson(Map<String, dynamic> json) =>
      _$CreatePracticeSessionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CreatePracticeSessionResponseToJson(this);

  @override
  List<Object?> get props => [success, sessionId, totalQuestions, mode, message];
}
