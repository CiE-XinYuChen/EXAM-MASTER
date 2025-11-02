// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'answer_record_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AnswerRecordModel _$AnswerRecordModelFromJson(Map<String, dynamic> json) =>
    AnswerRecordModel(
      id: json['id'] as String,
      userId: (json['user_id'] as num).toInt(),
      questionId: json['question_id'] as String,
      sessionId: json['session_id'] as String?,
      bankId: json['bank_id'] as String,
      userAnswer: json['user_answer'] as Map<String, dynamic>,
      isCorrect: json['is_correct'] as bool,
      timeSpent: (json['time_spent'] as num?)?.toInt(),
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$AnswerRecordModelToJson(AnswerRecordModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'question_id': instance.questionId,
      'session_id': instance.sessionId,
      'bank_id': instance.bankId,
      'user_answer': instance.userAnswer,
      'is_correct': instance.isCorrect,
      'time_spent': instance.timeSpent,
      'created_at': instance.createdAt,
    };

SubmitAnswerRequest _$SubmitAnswerRequestFromJson(Map<String, dynamic> json) =>
    SubmitAnswerRequest(
      userId: (json['user_id'] as num).toInt(),
      questionId: json['question_id'] as String,
      sessionId: json['session_id'] as String?,
      userAnswer: json['user_answer'] as Map<String, dynamic>,
      timeSpent: (json['time_spent'] as num?)?.toInt(),
    );

Map<String, dynamic> _$SubmitAnswerRequestToJson(
  SubmitAnswerRequest instance,
) => <String, dynamic>{
  'user_id': instance.userId,
  'question_id': instance.questionId,
  'session_id': instance.sessionId,
  'user_answer': instance.userAnswer,
  'time_spent': instance.timeSpent,
};

SubmitAnswerResponse _$SubmitAnswerResponseFromJson(
  Map<String, dynamic> json,
) => SubmitAnswerResponse(
  success: json['success'] as bool,
  isCorrect: json['is_correct'] as bool,
  correctAnswer: json['correct_answer'] as Map<String, dynamic>,
  explanation: json['explanation'] as String?,
  timeSpent: (json['time_spent'] as num?)?.toInt(),
  recordId: json['record_id'] as String,
);

Map<String, dynamic> _$SubmitAnswerResponseToJson(
  SubmitAnswerResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'is_correct': instance.isCorrect,
  'correct_answer': instance.correctAnswer,
  'explanation': instance.explanation,
  'time_spent': instance.timeSpent,
  'record_id': instance.recordId,
};

AnswerHistoryResponse _$AnswerHistoryResponseFromJson(
  Map<String, dynamic> json,
) => AnswerHistoryResponse(
  records: (json['records'] as List<dynamic>)
      .map((e) => AnswerRecordModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$AnswerHistoryResponseToJson(
  AnswerHistoryResponse instance,
) => <String, dynamic>{'records': instance.records, 'total': instance.total};
