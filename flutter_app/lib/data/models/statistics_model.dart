import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'statistics_model.g.dart';

/// Statistics Overview Model
/// 统计概览数据模型
@JsonSerializable()
class StatisticsOverviewModel extends Equatable {
  @JsonKey(name: 'total_banks_accessed')
  final int totalBanksAccessed;
  @JsonKey(name: 'total_questions_practiced')
  final int totalQuestionsPracticed;
  @JsonKey(name: 'total_correct')
  final int totalCorrect;
  @JsonKey(name: 'total_wrong')
  final int totalWrong;
  @JsonKey(name: 'overall_accuracy_rate')
  final double overallAccuracyRate;
  @JsonKey(name: 'total_time_spent')
  final int totalTimeSpent;
  @JsonKey(name: 'total_sessions')
  final int totalSessions;
  @JsonKey(name: 'total_favorites')
  final int totalFavorites;
  @JsonKey(name: 'total_wrong_questions')
  final int totalWrongQuestions;
  @JsonKey(name: 'consecutive_days')
  final int consecutiveDays;
  @JsonKey(name: 'total_practice_days')
  final int totalPracticeDays;

  const StatisticsOverviewModel({
    required this.totalBanksAccessed,
    required this.totalQuestionsPracticed,
    required this.totalCorrect,
    required this.totalWrong,
    required this.overallAccuracyRate,
    required this.totalTimeSpent,
    required this.totalSessions,
    required this.totalFavorites,
    required this.totalWrongQuestions,
    required this.consecutiveDays,
    required this.totalPracticeDays,
  });

  factory StatisticsOverviewModel.fromJson(Map<String, dynamic> json) =>
      _$StatisticsOverviewModelFromJson(json);

  Map<String, dynamic> toJson() => _$StatisticsOverviewModelToJson(this);

  @override
  List<Object?> get props => [
        totalBanksAccessed,
        totalQuestionsPracticed,
        totalCorrect,
        totalWrong,
        overallAccuracyRate,
        totalTimeSpent,
        totalSessions,
        totalFavorites,
        totalWrongQuestions,
        consecutiveDays,
        totalPracticeDays,
      ];
}

/// Bank Statistics Model
/// 题库统计数据模型
@JsonSerializable()
class BankStatisticsModel extends Equatable {
  @JsonKey(name: 'bank_id')
  final String bankId;
  @JsonKey(name: 'bank_name')
  final String? bankName;
  @JsonKey(name: 'total_questions')
  final int totalQuestions;
  @JsonKey(name: 'practiced_questions')
  final int practicedQuestions;
  @JsonKey(name: 'correct_count')
  final int correctCount;
  @JsonKey(name: 'wrong_count')
  final int wrongCount;
  @JsonKey(name: 'accuracy_rate')
  final double accuracyRate;
  @JsonKey(name: 'favorite_count')
  final int favoriteCount;
  @JsonKey(name: 'wrong_questions_count')
  final int wrongQuestionsCount;
  @JsonKey(name: 'total_time_spent')
  final int totalTimeSpent;

  const BankStatisticsModel({
    required this.bankId,
    this.bankName,
    required this.totalQuestions,
    required this.practicedQuestions,
    required this.correctCount,
    required this.wrongCount,
    required this.accuracyRate,
    required this.favoriteCount,
    required this.wrongQuestionsCount,
    required this.totalTimeSpent,
  });

  factory BankStatisticsModel.fromJson(Map<String, dynamic> json) =>
      _$BankStatisticsModelFromJson(json);

  Map<String, dynamic> toJson() => _$BankStatisticsModelToJson(this);

  @override
  List<Object?> get props => [
        bankId,
        bankName,
        totalQuestions,
        practicedQuestions,
        correctCount,
        wrongCount,
        accuracyRate,
        favoriteCount,
        wrongQuestionsCount,
        totalTimeSpent,
      ];

  /// Calculate progress percentage
  double get progressPercentage {
    if (totalQuestions == 0) return 0.0;
    return (practicedQuestions / totalQuestions) * 100;
  }
}

/// Daily Statistics Model
/// 每日统计数据模型
@JsonSerializable()
class DailyStatisticsModel extends Equatable {
  final String date;
  @JsonKey(name: 'questions_practiced')
  final int questionsPracticed;
  @JsonKey(name: 'correct_count')
  final int correctCount;
  @JsonKey(name: 'wrong_count')
  final int wrongCount;
  @JsonKey(name: 'accuracy_rate')
  final double accuracyRate;
  @JsonKey(name: 'time_spent')
  final int timeSpent;
  @JsonKey(name: 'sessions_count')
  final int sessionsCount;

  const DailyStatisticsModel({
    required this.date,
    required this.questionsPracticed,
    required this.correctCount,
    required this.wrongCount,
    required this.accuracyRate,
    required this.timeSpent,
    required this.sessionsCount,
  });

  factory DailyStatisticsModel.fromJson(Map<String, dynamic> json) =>
      _$DailyStatisticsModelFromJson(json);

  Map<String, dynamic> toJson() => _$DailyStatisticsModelToJson(this);

  @override
  List<Object?> get props => [
        date,
        questionsPracticed,
        correctCount,
        wrongCount,
        accuracyRate,
        timeSpent,
        sessionsCount,
      ];
}

/// Statistics Overview Response
@JsonSerializable()
class StatisticsOverviewResponse extends Equatable {
  final StatisticsOverviewModel statistics;

  const StatisticsOverviewResponse({
    required this.statistics,
  });

  factory StatisticsOverviewResponse.fromJson(Map<String, dynamic> json) =>
      _$StatisticsOverviewResponseFromJson(json);

  Map<String, dynamic> toJson() => _$StatisticsOverviewResponseToJson(this);

  @override
  List<Object?> get props => [statistics];
}

/// Bank Statistics List Response
@JsonSerializable()
class BankStatisticsListResponse extends Equatable {
  @JsonKey(name: 'bank_stats')
  final List<BankStatisticsModel> bankStats;

  const BankStatisticsListResponse({
    required this.bankStats,
  });

  factory BankStatisticsListResponse.fromJson(Map<String, dynamic> json) =>
      _$BankStatisticsListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$BankStatisticsListResponseToJson(this);

  @override
  List<Object?> get props => [bankStats];
}

/// Daily Statistics List Response
@JsonSerializable()
class DailyStatisticsListResponse extends Equatable {
  @JsonKey(name: 'daily_stats')
  final List<DailyStatisticsModel> dailyStats;

  const DailyStatisticsListResponse({
    required this.dailyStats,
  });

  factory DailyStatisticsListResponse.fromJson(Map<String, dynamic> json) =>
      _$DailyStatisticsListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$DailyStatisticsListResponseToJson(this);

  @override
  List<Object?> get props => [dailyStats];
}

// Type alias for single bank statistics
typedef BankStatisticsResponse = BankStatisticsModel;
