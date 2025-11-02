import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'answer_record_model.g.dart';

/// Answer Record Model
/// 答题记录数据模型
@JsonSerializable()
class AnswerRecordModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'question_id')
  final String questionId;
  @JsonKey(name: 'session_id')
  final String? sessionId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  @JsonKey(name: 'user_answer')
  final Map<String, dynamic> userAnswer;
  @JsonKey(name: 'is_correct')
  final bool isCorrect;
  @JsonKey(name: 'time_spent')
  final int? timeSpent;
  @JsonKey(name: 'created_at')
  final String createdAt;

  const AnswerRecordModel({
    required this.id,
    required this.userId,
    required this.questionId,
    this.sessionId,
    required this.bankId,
    required this.userAnswer,
    required this.isCorrect,
    this.timeSpent,
    required this.createdAt,
  });

  factory AnswerRecordModel.fromJson(Map<String, dynamic> json) =>
      _$AnswerRecordModelFromJson(json);

  Map<String, dynamic> toJson() => _$AnswerRecordModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        questionId,
        sessionId,
        bankId,
        userAnswer,
        isCorrect,
        timeSpent,
        createdAt,
      ];
}

/// Submit Answer Request
@JsonSerializable()
class SubmitAnswerRequest {
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'question_id')
  final String questionId;
  @JsonKey(name: 'session_id')
  final String? sessionId;
  @JsonKey(name: 'user_answer')
  final Map<String, dynamic> userAnswer;
  @JsonKey(name: 'time_spent')
  final int? timeSpent;

  const SubmitAnswerRequest({
    required this.userId,
    required this.questionId,
    this.sessionId,
    required this.userAnswer,
    this.timeSpent,
  });

  Map<String, dynamic> toJson() => _$SubmitAnswerRequestToJson(this);
}

/// Submit Answer Response
@JsonSerializable()
class SubmitAnswerResponse extends Equatable {
  final bool success;
  @JsonKey(name: 'is_correct')
  final bool isCorrect;
  @JsonKey(name: 'correct_answer')
  final Map<String, dynamic> correctAnswer;
  final String? explanation;
  @JsonKey(name: 'time_spent')
  final int? timeSpent;
  @JsonKey(name: 'record_id')
  final String recordId;

  const SubmitAnswerResponse({
    required this.success,
    required this.isCorrect,
    required this.correctAnswer,
    this.explanation,
    this.timeSpent,
    required this.recordId,
  });

  factory SubmitAnswerResponse.fromJson(Map<String, dynamic> json) =>
      _$SubmitAnswerResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SubmitAnswerResponseToJson(this);

  @override
  List<Object?> get props => [
        success,
        isCorrect,
        correctAnswer,
        explanation,
        timeSpent,
        recordId,
      ];
}

/// Answer History Response
@JsonSerializable()
class AnswerHistoryResponse extends Equatable {
  final List<AnswerRecordModel> records;
  final int total;

  const AnswerHistoryResponse({
    required this.records,
    required this.total,
  });

  factory AnswerHistoryResponse.fromJson(Map<String, dynamic> json) =>
      _$AnswerHistoryResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AnswerHistoryResponseToJson(this);

  @override
  List<Object?> get props => [records, total];
}
