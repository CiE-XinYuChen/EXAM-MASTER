import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'favorite_model.g.dart';

/// Question Option Model
/// 题目选项模型
@JsonSerializable()
class QuestionOption extends Equatable {
  final String label;
  final String content;
  @JsonKey(name: 'is_correct')
  final bool? isCorrect;

  const QuestionOption({
    required this.label,
    required this.content,
    this.isCorrect,
  });

  factory QuestionOption.fromJson(Map<String, dynamic> json) =>
      _$QuestionOptionFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionOptionToJson(this);

  @override
  List<Object?> get props => [label, content, isCorrect];
}

/// Favorite Model
/// 收藏数据模型（带题目详细信息）
@JsonSerializable()
class FavoriteModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'question_id')
  final String questionId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  final String? note;
  @JsonKey(name: 'created_at')
  final String createdAt;

  // Question details from backend
  @JsonKey(name: 'question_number')
  final int? questionNumber;
  @JsonKey(name: 'question_type')
  final String questionType;
  @JsonKey(name: 'question_stem')
  final String questionStem;
  @JsonKey(name: 'question_difficulty')
  final String? questionDifficulty;
  @JsonKey(name: 'question_tags')
  final List<String>? questionTags;
  @JsonKey(name: 'question_options')
  final List<QuestionOption>? questionOptions;
  @JsonKey(name: 'question_explanation')
  final String? questionExplanation;
  @JsonKey(name: 'correct_answer')
  final Map<String, dynamic>? correctAnswer;
  @JsonKey(name: 'has_image')
  final bool? hasImage;
  @JsonKey(name: 'has_video')
  final bool? hasVideo;
  @JsonKey(name: 'has_audio')
  final bool? hasAudio;

  const FavoriteModel({
    required this.id,
    required this.userId,
    required this.questionId,
    required this.bankId,
    this.note,
    required this.createdAt,
    this.questionNumber,
    required this.questionType,
    required this.questionStem,
    this.questionDifficulty,
    this.questionTags,
    this.questionOptions,
    this.questionExplanation,
    this.correctAnswer,
    this.hasImage,
    this.hasVideo,
    this.hasAudio,
  });

  factory FavoriteModel.fromJson(Map<String, dynamic> json) =>
      _$FavoriteModelFromJson(json);

  Map<String, dynamic> toJson() => _$FavoriteModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        questionId,
        bankId,
        note,
        createdAt,
        questionNumber,
        questionType,
        questionStem,
        questionDifficulty,
        questionTags,
        questionOptions,
        questionExplanation,
        correctAnswer,
        hasImage,
        hasVideo,
        hasAudio,
      ];

  FavoriteModel copyWith({
    String? id,
    int? userId,
    String? questionId,
    String? bankId,
    String? note,
    String? createdAt,
    String? questionType,
    String? questionStem,
    String? questionDifficulty,
    List<String>? questionTags,
    List<QuestionOption>? questionOptions,
    String? questionExplanation,
    Map<String, dynamic>? correctAnswer,
    bool? hasImage,
    bool? hasVideo,
    bool? hasAudio,
  }) {
    return FavoriteModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      questionId: questionId ?? this.questionId,
      bankId: bankId ?? this.bankId,
      note: note ?? this.note,
      createdAt: createdAt ?? this.createdAt,
      questionType: questionType ?? this.questionType,
      questionStem: questionStem ?? this.questionStem,
      questionDifficulty: questionDifficulty ?? this.questionDifficulty,
      questionTags: questionTags ?? this.questionTags,
      questionOptions: questionOptions ?? this.questionOptions,
      questionExplanation: questionExplanation ?? this.questionExplanation,
      correctAnswer: correctAnswer ?? this.correctAnswer,
      hasImage: hasImage ?? this.hasImage,
      hasVideo: hasVideo ?? this.hasVideo,
      hasAudio: hasAudio ?? this.hasAudio,
    );
  }
}

/// Add Favorite Request
@JsonSerializable()
class AddFavoriteRequest {
  @JsonKey(name: 'question_id')
  final String questionId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  final String? note;

  const AddFavoriteRequest({
    required this.questionId,
    required this.bankId,
    this.note,
  });

  Map<String, dynamic> toJson() => _$AddFavoriteRequestToJson(this);
}

/// Add Favorite Response
@JsonSerializable()
class AddFavoriteResponse extends Equatable {
  final bool success;
  @JsonKey(name: 'favorite_id')
  final String favoriteId;
  final String? message;

  const AddFavoriteResponse({
    required this.success,
    required this.favoriteId,
    this.message,
  });

  factory AddFavoriteResponse.fromJson(Map<String, dynamic> json) =>
      _$AddFavoriteResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AddFavoriteResponseToJson(this);

  @override
  List<Object?> get props => [success, favoriteId, message];
}

/// Favorite List Response
@JsonSerializable()
class FavoriteListResponse extends Equatable {
  final List<FavoriteModel> favorites;
  final int total;

  const FavoriteListResponse({
    required this.favorites,
    required this.total,
  });

  factory FavoriteListResponse.fromJson(Map<String, dynamic> json) =>
      _$FavoriteListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$FavoriteListResponseToJson(this);

  @override
  List<Object?> get props => [favorites, total];
}

/// Update Favorite Note Request
@JsonSerializable()
class UpdateFavoriteNoteRequest {
  final String note;

  const UpdateFavoriteNoteRequest({
    required this.note,
  });

  Map<String, dynamic> toJson() => _$UpdateFavoriteNoteRequestToJson(this);
}
