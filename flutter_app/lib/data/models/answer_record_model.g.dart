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

AnswerOptionResult _$AnswerOptionResultFromJson(Map<String, dynamic> json) =>
    AnswerOptionResult(
      label: json['label'] as String,
      content: json['content'] as String,
      isCorrect: json['is_correct'] as bool,
    );

Map<String, dynamic> _$AnswerOptionResultToJson(AnswerOptionResult instance) =>
    <String, dynamic>{
      'label': instance.label,
      'content': instance.content,
      'is_correct': instance.isCorrect,
    };

SubmitAnswerResponse _$SubmitAnswerResponseFromJson(
  Map<String, dynamic> json,
) => SubmitAnswerResponse(
  recordId: json['record_id'] as String,
  questionId: json['question_id'] as String,
  isCorrect: json['is_correct'] as bool,
  correctAnswer: json['correct_answer'] as Map<String, dynamic>,
  userAnswer: json['user_answer'] as Map<String, dynamic>,
  explanation: json['explanation'] as String?,
  timeSpent: (json['time_spent'] as num?)?.toInt(),
  createdAt: json['created_at'] as String,
  options: (json['options'] as List<dynamic>?)
      ?.map((e) => AnswerOptionResult.fromJson(e as Map<String, dynamic>))
      .toList(),
  questionType: json['question_type'] as String?,
  questionStem: json['question_stem'] as String?,
);

Map<String, dynamic> _$SubmitAnswerResponseToJson(
  SubmitAnswerResponse instance,
) => <String, dynamic>{
  'record_id': instance.recordId,
  'question_id': instance.questionId,
  'is_correct': instance.isCorrect,
  'correct_answer': instance.correctAnswer,
  'user_answer': instance.userAnswer,
  'explanation': instance.explanation,
  'time_spent': instance.timeSpent,
  'created_at': instance.createdAt,
  'options': instance.options,
  'question_type': instance.questionType,
  'question_stem': instance.questionStem,
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
