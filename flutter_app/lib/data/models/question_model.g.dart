// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'question_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

QuestionOptionModel _$QuestionOptionModelFromJson(Map<String, dynamic> json) =>
    QuestionOptionModel(
      label: json['option_label'] as String,
      content: json['option_content'] as String,
      isCorrect: json['is_correct'] as bool?,
    );

Map<String, dynamic> _$QuestionOptionModelToJson(
  QuestionOptionModel instance,
) => <String, dynamic>{
  'option_label': instance.label,
  'option_content': instance.content,
  'is_correct': instance.isCorrect,
};

QuestionModel _$QuestionModelFromJson(Map<String, dynamic> json) =>
    QuestionModel(
      id: json['id'] as String,
      bankId: json['bank_id'] as String,
      type: $enumDecode(_$QuestionTypeEnumMap, json['type']),
      stem: json['stem'] as String,
      options: (json['options'] as List<dynamic>?)
          ?.map((e) => QuestionOptionModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      difficulty: $enumDecodeNullable(
        _$QuestionDifficultyEnumMap,
        json['difficulty'],
      ),
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      correctAnswer: json['correct_answer'] as Map<String, dynamic>?,
      explanation: json['explanation'] as String?,
      hasImage: json['has_image'] as bool?,
      hasVideo: json['has_video'] as bool?,
      hasAudio: json['has_audio'] as bool?,
      isFavorite: json['is_favorite'] as bool?,
      isInWrongBook: json['is_in_wrong_book'] as bool?,
      errorCount: (json['error_count'] as num?)?.toInt(),
    );

Map<String, dynamic> _$QuestionModelToJson(QuestionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'bank_id': instance.bankId,
      'type': _$QuestionTypeEnumMap[instance.type]!,
      'stem': instance.stem,
      'options': instance.options,
      'difficulty': _$QuestionDifficultyEnumMap[instance.difficulty],
      'tags': instance.tags,
      'correct_answer': instance.correctAnswer,
      'explanation': instance.explanation,
      'has_image': instance.hasImage,
      'has_video': instance.hasVideo,
      'has_audio': instance.hasAudio,
      'is_favorite': instance.isFavorite,
      'is_in_wrong_book': instance.isInWrongBook,
      'error_count': instance.errorCount,
    };

const _$QuestionTypeEnumMap = {
  QuestionType.single: 'single',
  QuestionType.multiple: 'multiple',
  QuestionType.judge: 'judge',
  QuestionType.fill: 'fill',
  QuestionType.essay: 'essay',
  QuestionType.composite: 'composite',
};

const _$QuestionDifficultyEnumMap = {
  QuestionDifficulty.easy: 'easy',
  QuestionDifficulty.medium: 'medium',
  QuestionDifficulty.hard: 'hard',
  QuestionDifficulty.expert: 'expert',
};

QuestionListResponse _$QuestionListResponseFromJson(
  Map<String, dynamic> json,
) => QuestionListResponse(
  questions: (json['questions'] as List<dynamic>)
      .map((e) => QuestionModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$QuestionListResponseToJson(
  QuestionListResponse instance,
) => <String, dynamic>{
  'questions': instance.questions,
  'total': instance.total,
};
