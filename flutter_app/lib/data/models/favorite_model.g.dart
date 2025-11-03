// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'favorite_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FavoriteModel _$FavoriteModelFromJson(Map<String, dynamic> json) =>
    FavoriteModel(
      id: json['id'] as String,
      userId: (json['user_id'] as num).toInt(),
      questionId: json['question_id'] as String,
      bankId: json['bank_id'] as String,
      note: json['note'] as String?,
      createdAt: json['created_at'] as String,
      question: json['question'] == null
          ? null
          : QuestionModel.fromJson(json['question'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$FavoriteModelToJson(FavoriteModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'question_id': instance.questionId,
      'bank_id': instance.bankId,
      'note': instance.note,
      'created_at': instance.createdAt,
      'question': instance.question,
    };

AddFavoriteRequest _$AddFavoriteRequestFromJson(Map<String, dynamic> json) =>
    AddFavoriteRequest(
      questionId: json['question_id'] as String,
      bankId: json['bank_id'] as String,
      note: json['note'] as String?,
    );

Map<String, dynamic> _$AddFavoriteRequestToJson(AddFavoriteRequest instance) =>
    <String, dynamic>{
      'question_id': instance.questionId,
      'bank_id': instance.bankId,
      'note': instance.note,
    };

AddFavoriteResponse _$AddFavoriteResponseFromJson(Map<String, dynamic> json) =>
    AddFavoriteResponse(
      success: json['success'] as bool,
      favoriteId: json['favorite_id'] as String,
      message: json['message'] as String?,
    );

Map<String, dynamic> _$AddFavoriteResponseToJson(
  AddFavoriteResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'favorite_id': instance.favoriteId,
  'message': instance.message,
};

FavoriteListResponse _$FavoriteListResponseFromJson(
  Map<String, dynamic> json,
) => FavoriteListResponse(
  favorites: (json['favorites'] as List<dynamic>)
      .map((e) => FavoriteModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$FavoriteListResponseToJson(
  FavoriteListResponse instance,
) => <String, dynamic>{
  'favorites': instance.favorites,
  'total': instance.total,
};

UpdateFavoriteNoteRequest _$UpdateFavoriteNoteRequestFromJson(
  Map<String, dynamic> json,
) => UpdateFavoriteNoteRequest(note: json['note'] as String);

Map<String, dynamic> _$UpdateFavoriteNoteRequestToJson(
  UpdateFavoriteNoteRequest instance,
) => <String, dynamic>{'note': instance.note};
