// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'question_bank_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

QuestionBankModel _$QuestionBankModelFromJson(Map<String, dynamic> json) =>
    QuestionBankModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      category: json['category'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      isPublic: json['is_public'] as bool?,
      totalQuestions: (json['total_questions'] as num?)?.toInt(),
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
    );

Map<String, dynamic> _$QuestionBankModelToJson(QuestionBankModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'category': instance.category,
      'tags': instance.tags,
      'is_public': instance.isPublic,
      'total_questions': instance.totalQuestions,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

QuestionBankListResponse _$QuestionBankListResponseFromJson(
  Map<String, dynamic> json,
) => QuestionBankListResponse(
  banks: (json['banks'] as List<dynamic>)
      .map((e) => QuestionBankModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$QuestionBankListResponseToJson(
  QuestionBankListResponse instance,
) => <String, dynamic>{'banks': instance.banks, 'total': instance.total};
