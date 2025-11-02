// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'practice_session_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PracticeSessionModel _$PracticeSessionModelFromJson(
  Map<String, dynamic> json,
) => PracticeSessionModel(
  id: json['id'] as String,
  userId: (json['user_id'] as num).toInt(),
  bankId: json['bank_id'] as String,
  mode: $enumDecode(_$PracticeModeEnumMap, json['mode']),
  totalQuestions: (json['total_questions'] as num).toInt(),
  currentIndex: (json['current_index'] as num).toInt(),
  completedCount: (json['completed_count'] as num).toInt(),
  correctCount: (json['correct_count'] as num).toInt(),
  status: $enumDecode(_$SessionStatusEnumMap, json['status']),
  questionIds: (json['question_ids'] as List<dynamic>?)
      ?.map((e) => e as String)
      .toList(),
  startedAt: json['started_at'] as String,
  completedAt: json['completed_at'] as String?,
  lastActivityAt: json['last_activity_at'] as String?,
);

Map<String, dynamic> _$PracticeSessionModelToJson(
  PracticeSessionModel instance,
) => <String, dynamic>{
  'id': instance.id,
  'user_id': instance.userId,
  'bank_id': instance.bankId,
  'mode': _$PracticeModeEnumMap[instance.mode]!,
  'total_questions': instance.totalQuestions,
  'current_index': instance.currentIndex,
  'completed_count': instance.completedCount,
  'correct_count': instance.correctCount,
  'status': _$SessionStatusEnumMap[instance.status]!,
  'question_ids': instance.questionIds,
  'started_at': instance.startedAt,
  'completed_at': instance.completedAt,
  'last_activity_at': instance.lastActivityAt,
};

const _$PracticeModeEnumMap = {
  PracticeMode.sequential: 'sequential',
  PracticeMode.random: 'random',
  PracticeMode.wrongOnly: 'wrong_only',
  PracticeMode.favoriteOnly: 'favorite_only',
  PracticeMode.unpracticed: 'unpracticed',
};

const _$SessionStatusEnumMap = {
  SessionStatus.inProgress: 'in_progress',
  SessionStatus.completed: 'completed',
  SessionStatus.paused: 'paused',
};

CreatePracticeSessionRequest _$CreatePracticeSessionRequestFromJson(
  Map<String, dynamic> json,
) => CreatePracticeSessionRequest(
  bankId: json['bank_id'] as String,
  mode: json['mode'] as String,
  questionTypes: (json['question_types'] as List<dynamic>?)
      ?.map((e) => e as String)
      .toList(),
  difficulty: json['difficulty'] as String?,
);

Map<String, dynamic> _$CreatePracticeSessionRequestToJson(
  CreatePracticeSessionRequest instance,
) => <String, dynamic>{
  'bank_id': instance.bankId,
  'mode': instance.mode,
  'question_types': instance.questionTypes,
  'difficulty': instance.difficulty,
};

CreatePracticeSessionResponse _$CreatePracticeSessionResponseFromJson(
  Map<String, dynamic> json,
) => CreatePracticeSessionResponse(
  success: json['success'] as bool,
  sessionId: json['session_id'] as String,
  totalQuestions: (json['total_questions'] as num).toInt(),
  mode: json['mode'] as String,
  message: json['message'] as String?,
);

Map<String, dynamic> _$CreatePracticeSessionResponseToJson(
  CreatePracticeSessionResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'session_id': instance.sessionId,
  'total_questions': instance.totalQuestions,
  'mode': instance.mode,
  'message': instance.message,
};
