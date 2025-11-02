// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'wrong_question_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WrongQuestionModel _$WrongQuestionModelFromJson(Map<String, dynamic> json) =>
    WrongQuestionModel(
      id: json['id'] as String,
      userId: (json['user_id'] as num).toInt(),
      questionId: json['question_id'] as String,
      bankId: json['bank_id'] as String,
      errorCount: (json['error_count'] as num).toInt(),
      lastErrorAnswer: json['last_error_answer'] as Map<String, dynamic>?,
      corrected: json['corrected'] as bool,
      firstErrorAt: json['first_error_at'] as String,
      lastErrorAt: json['last_error_at'] as String,
      correctedAt: json['corrected_at'] as String?,
      question: json['question'] == null
          ? null
          : QuestionModel.fromJson(json['question'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$WrongQuestionModelToJson(WrongQuestionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'question_id': instance.questionId,
      'bank_id': instance.bankId,
      'error_count': instance.errorCount,
      'last_error_answer': instance.lastErrorAnswer,
      'corrected': instance.corrected,
      'first_error_at': instance.firstErrorAt,
      'last_error_at': instance.lastErrorAt,
      'corrected_at': instance.correctedAt,
      'question': instance.question,
    };

WrongQuestionListResponse _$WrongQuestionListResponseFromJson(
  Map<String, dynamic> json,
) => WrongQuestionListResponse(
  wrongQuestions: (json['wrong_questions'] as List<dynamic>)
      .map((e) => WrongQuestionModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$WrongQuestionListResponseToJson(
  WrongQuestionListResponse instance,
) => <String, dynamic>{
  'wrong_questions': instance.wrongQuestions,
  'total': instance.total,
};

WrongQuestionAnalysisModel _$WrongQuestionAnalysisModelFromJson(
  Map<String, dynamic> json,
) => WrongQuestionAnalysisModel(
  totalWrongQuestions: (json['total_wrong_questions'] as num).toInt(),
  correctedCount: (json['corrected_count'] as num).toInt(),
  uncorrectedCount: (json['uncorrected_count'] as num).toInt(),
  byDifficulty: Map<String, int>.from(json['by_difficulty'] as Map),
  byType: Map<String, int>.from(json['by_type'] as Map),
  topErrorQuestions: (json['top_error_questions'] as List<dynamic>)
      .map((e) => WrongQuestionModel.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$WrongQuestionAnalysisModelToJson(
  WrongQuestionAnalysisModel instance,
) => <String, dynamic>{
  'total_wrong_questions': instance.totalWrongQuestions,
  'corrected_count': instance.correctedCount,
  'uncorrected_count': instance.uncorrectedCount,
  'by_difficulty': instance.byDifficulty,
  'by_type': instance.byType,
  'top_error_questions': instance.topErrorQuestions,
};

MarkCorrectedResponse _$MarkCorrectedResponseFromJson(
  Map<String, dynamic> json,
) => MarkCorrectedResponse(
  success: json['success'] as bool,
  message: json['message'] as String?,
);

Map<String, dynamic> _$MarkCorrectedResponseToJson(
  MarkCorrectedResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'message': instance.message,
};
