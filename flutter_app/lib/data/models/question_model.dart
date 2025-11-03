import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'question_model.g.dart';

/// Question Type Enum
enum QuestionType {
  @JsonValue('single')
  single,
  @JsonValue('multiple')
  multiple,
  @JsonValue('judge')
  judge,
  @JsonValue('fill')
  fill,
  @JsonValue('essay')
  essay,
}

/// Question Difficulty Enum
enum QuestionDifficulty {
  @JsonValue('easy')
  easy,
  @JsonValue('medium')
  medium,
  @JsonValue('hard')
  hard,
  @JsonValue('expert')
  expert,
}

/// Question Option Model
/// 题目选项模型
@JsonSerializable()
class QuestionOptionModel extends Equatable {
  @JsonKey(name: 'option_label')
  final String label;
  @JsonKey(name: 'option_content')
  final String content;
  @JsonKey(name: 'is_correct')
  final bool? isCorrect;

  const QuestionOptionModel({
    required this.label,
    required this.content,
    this.isCorrect,
  });

  factory QuestionOptionModel.fromJson(Map<String, dynamic> json) =>
      _$QuestionOptionModelFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionOptionModelToJson(this);

  @override
  List<Object?> get props => [label, content, isCorrect];
}

/// Question Model
/// 题目数据模型
@JsonSerializable()
class QuestionModel extends Equatable {
  final String id;
  @JsonKey(name: 'bank_id')
  final String bankId;
  final QuestionType type;
  final String stem;
  final List<QuestionOptionModel>? options;
  final QuestionDifficulty? difficulty;
  final List<String>? tags;
  @JsonKey(name: 'correct_answer')
  final Map<String, dynamic>? correctAnswer;
  final String? explanation;
  @JsonKey(name: 'has_image')
  final bool? hasImage;
  @JsonKey(name: 'has_video')
  final bool? hasVideo;
  @JsonKey(name: 'has_audio')
  final bool? hasAudio;
  @JsonKey(name: 'is_favorite')
  final bool? isFavorite;
  @JsonKey(name: 'is_in_wrong_book')
  final bool? isInWrongBook;
  @JsonKey(name: 'error_count')
  final int? errorCount;

  const QuestionModel({
    required this.id,
    required this.bankId,
    required this.type,
    required this.stem,
    this.options,
    this.difficulty,
    this.tags,
    this.correctAnswer,
    this.explanation,
    this.hasImage,
    this.hasVideo,
    this.hasAudio,
    this.isFavorite,
    this.isInWrongBook,
    this.errorCount,
  });

  factory QuestionModel.fromJson(Map<String, dynamic> json) =>
      _$QuestionModelFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        bankId,
        type,
        stem,
        options,
        difficulty,
        tags,
        correctAnswer,
        explanation,
        hasImage,
        hasVideo,
        hasAudio,
        isFavorite,
        isInWrongBook,
        errorCount,
      ];

  QuestionModel copyWith({
    String? id,
    String? bankId,
    QuestionType? type,
    String? stem,
    List<QuestionOptionModel>? options,
    QuestionDifficulty? difficulty,
    List<String>? tags,
    Map<String, dynamic>? correctAnswer,
    String? explanation,
    bool? hasImage,
    bool? hasVideo,
    bool? hasAudio,
    bool? isFavorite,
    bool? isInWrongBook,
    int? errorCount,
  }) {
    return QuestionModel(
      id: id ?? this.id,
      bankId: bankId ?? this.bankId,
      type: type ?? this.type,
      stem: stem ?? this.stem,
      options: options ?? this.options,
      difficulty: difficulty ?? this.difficulty,
      tags: tags ?? this.tags,
      correctAnswer: correctAnswer ?? this.correctAnswer,
      explanation: explanation ?? this.explanation,
      hasImage: hasImage ?? this.hasImage,
      hasVideo: hasVideo ?? this.hasVideo,
      hasAudio: hasAudio ?? this.hasAudio,
      isFavorite: isFavorite ?? this.isFavorite,
      isInWrongBook: isInWrongBook ?? this.isInWrongBook,
      errorCount: errorCount ?? this.errorCount,
    );
  }

  /// Get correct answer based on question type
  String? getCorrectAnswerText() {
    if (correctAnswer == null) return null;

    switch (type) {
      case QuestionType.single:
        return correctAnswer!['answer'] as String?;
      case QuestionType.multiple:
        final answers = correctAnswer!['answers'] as List<dynamic>?;
        return answers?.join(', ');
      case QuestionType.judge:
        return correctAnswer!['answer'] == 'true' ? '正确' : '错误';
      case QuestionType.fill:
        final answers = correctAnswer!['fill_answers'] as List<dynamic>?;
        return answers?.join(', ');
      case QuestionType.essay:
        return correctAnswer!['essay_answer'] as String?;
    }
  }

  /// Check if answer is correct
  bool checkAnswer(dynamic userAnswer) {
    if (correctAnswer == null) return false;

    switch (type) {
      case QuestionType.single:
        return userAnswer == correctAnswer!['answer'];
      case QuestionType.multiple:
        final correct = Set.from(correctAnswer!['answers'] as List);
        final user = Set.from(userAnswer as List);
        return correct.difference(user).isEmpty &&
            user.difference(correct).isEmpty;
      case QuestionType.judge:
        return userAnswer.toString() == correctAnswer!['answer'];
      case QuestionType.fill:
      case QuestionType.essay:
        // These require server-side validation
        return false;
    }
  }
}

/// Question List Response
@JsonSerializable()
class QuestionListResponse extends Equatable {
  final List<QuestionModel> questions;
  final int total;

  const QuestionListResponse({
    required this.questions,
    required this.total,
  });

  factory QuestionListResponse.fromJson(Map<String, dynamic> json) =>
      _$QuestionListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionListResponseToJson(this);

  @override
  List<Object?> get props => [questions, total];
}
