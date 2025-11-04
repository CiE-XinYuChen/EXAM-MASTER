import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'wrong_question_model.g.dart';

/// Wrong Question Model
/// 错题数据模型
@JsonSerializable()
class WrongQuestionModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'question_id')
  final String questionId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  @JsonKey(name: 'error_count')
  final int errorCount;
  @JsonKey(name: 'last_error_answer')
  final Map<String, dynamic>? lastErrorAnswer;
  final bool corrected;
  @JsonKey(name: 'first_error_at')
  final String firstErrorAt;
  @JsonKey(name: 'last_error_at')
  final String lastErrorAt;
  @JsonKey(name: 'corrected_at')
  final String? correctedAt;

  // Question details from backend (like FavoriteModel)
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
  @JsonKey(name: 'has_image')
  final bool? hasImage;
  @JsonKey(name: 'has_video')
  final bool? hasVideo;
  @JsonKey(name: 'has_audio')
  final bool? hasAudio;
  @JsonKey(name: 'correct_answer')
  final Map<String, dynamic>? correctAnswer;

  const WrongQuestionModel({
    required this.id,
    required this.userId,
    required this.questionId,
    required this.bankId,
    required this.errorCount,
    this.lastErrorAnswer,
    required this.corrected,
    required this.firstErrorAt,
    required this.lastErrorAt,
    this.correctedAt,
    this.questionNumber,
    required this.questionType,
    required this.questionStem,
    this.questionDifficulty,
    this.questionTags,
    this.hasImage,
    this.hasVideo,
    this.hasAudio,
    this.correctAnswer,
  });

  factory WrongQuestionModel.fromJson(Map<String, dynamic> json) =>
      _$WrongQuestionModelFromJson(json);

  Map<String, dynamic> toJson() => _$WrongQuestionModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        questionId,
        bankId,
        errorCount,
        lastErrorAnswer,
        corrected,
        firstErrorAt,
        lastErrorAt,
        correctedAt,
        questionNumber,
        questionType,
        questionStem,
        questionDifficulty,
        questionTags,
        hasImage,
        hasVideo,
        hasAudio,
        correctAnswer,
      ];

  WrongQuestionModel copyWith({
    String? id,
    int? userId,
    String? questionId,
    String? bankId,
    int? errorCount,
    Map<String, dynamic>? lastErrorAnswer,
    bool? corrected,
    String? firstErrorAt,
    String? lastErrorAt,
    String? correctedAt,
    String? questionType,
    String? questionStem,
    String? questionDifficulty,
    List<String>? questionTags,
    bool? hasImage,
    bool? hasVideo,
    bool? hasAudio,
    Map<String, dynamic>? correctAnswer,
  }) {
    return WrongQuestionModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      questionId: questionId ?? this.questionId,
      bankId: bankId ?? this.bankId,
      errorCount: errorCount ?? this.errorCount,
      lastErrorAnswer: lastErrorAnswer ?? this.lastErrorAnswer,
      corrected: corrected ?? this.corrected,
      firstErrorAt: firstErrorAt ?? this.firstErrorAt,
      lastErrorAt: lastErrorAt ?? this.lastErrorAt,
      correctedAt: correctedAt ?? this.correctedAt,
      questionType: questionType ?? this.questionType,
      questionStem: questionStem ?? this.questionStem,
      questionDifficulty: questionDifficulty ?? this.questionDifficulty,
      questionTags: questionTags ?? this.questionTags,
      hasImage: hasImage ?? this.hasImage,
      hasVideo: hasVideo ?? this.hasVideo,
      hasAudio: hasAudio ?? this.hasAudio,
      correctAnswer: correctAnswer ?? this.correctAnswer,
    );
  }
}

/// Wrong Question List Response
@JsonSerializable()
class WrongQuestionListResponse extends Equatable {
  @JsonKey(name: 'wrong_questions')
  final List<WrongQuestionModel> wrongQuestions;
  final int total;
  @JsonKey(name: 'uncorrected_count')
  final int uncorrectedCount;

  const WrongQuestionListResponse({
    required this.wrongQuestions,
    required this.total,
    required this.uncorrectedCount,
  });

  factory WrongQuestionListResponse.fromJson(Map<String, dynamic> json) =>
      _$WrongQuestionListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$WrongQuestionListResponseToJson(this);

  @override
  List<Object?> get props => [wrongQuestions, total, uncorrectedCount];
}

/// Wrong Question Analysis Model
@JsonSerializable()
class WrongQuestionAnalysisModel extends Equatable {
  @JsonKey(name: 'total_wrong_questions')
  final int totalWrongQuestions;
  @JsonKey(name: 'corrected_count')
  final int correctedCount;
  @JsonKey(name: 'uncorrected_count')
  final int uncorrectedCount;
  @JsonKey(name: 'by_difficulty')
  final Map<String, int> byDifficulty;
  @JsonKey(name: 'by_type')
  final Map<String, int> byType;
  @JsonKey(name: 'top_error_questions')
  final List<WrongQuestionModel> topErrorQuestions;

  const WrongQuestionAnalysisModel({
    required this.totalWrongQuestions,
    required this.correctedCount,
    required this.uncorrectedCount,
    required this.byDifficulty,
    required this.byType,
    required this.topErrorQuestions,
  });

  factory WrongQuestionAnalysisModel.fromJson(Map<String, dynamic> json) =>
      _$WrongQuestionAnalysisModelFromJson(json);

  Map<String, dynamic> toJson() => _$WrongQuestionAnalysisModelToJson(this);

  @override
  List<Object?> get props => [
        totalWrongQuestions,
        correctedCount,
        uncorrectedCount,
        byDifficulty,
        byType,
        topErrorQuestions,
      ];
}

/// Mark Wrong Question Corrected Response
@JsonSerializable()
class MarkCorrectedResponse extends Equatable {
  final bool success;
  final String? message;

  const MarkCorrectedResponse({
    required this.success,
    this.message,
  });

  factory MarkCorrectedResponse.fromJson(Map<String, dynamic> json) =>
      _$MarkCorrectedResponseFromJson(json);

  Map<String, dynamic> toJson() => _$MarkCorrectedResponseToJson(this);

  @override
  List<Object?> get props => [success, message];
}
