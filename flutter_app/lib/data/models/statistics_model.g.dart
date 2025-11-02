// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'statistics_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StatisticsOverviewModel _$StatisticsOverviewModelFromJson(
  Map<String, dynamic> json,
) => StatisticsOverviewModel(
  totalBanksAccessed: (json['total_banks_accessed'] as num).toInt(),
  totalQuestionsPracticed: (json['total_questions_practiced'] as num).toInt(),
  totalCorrect: (json['total_correct'] as num).toInt(),
  totalWrong: (json['total_wrong'] as num).toInt(),
  overallAccuracyRate: (json['overall_accuracy_rate'] as num).toDouble(),
  totalTimeSpent: (json['total_time_spent'] as num).toInt(),
  totalSessions: (json['total_sessions'] as num).toInt(),
  totalFavorites: (json['total_favorites'] as num).toInt(),
  totalWrongQuestions: (json['total_wrong_questions'] as num).toInt(),
  consecutiveDays: (json['consecutive_days'] as num).toInt(),
  totalPracticeDays: (json['total_practice_days'] as num).toInt(),
);

Map<String, dynamic> _$StatisticsOverviewModelToJson(
  StatisticsOverviewModel instance,
) => <String, dynamic>{
  'total_banks_accessed': instance.totalBanksAccessed,
  'total_questions_practiced': instance.totalQuestionsPracticed,
  'total_correct': instance.totalCorrect,
  'total_wrong': instance.totalWrong,
  'overall_accuracy_rate': instance.overallAccuracyRate,
  'total_time_spent': instance.totalTimeSpent,
  'total_sessions': instance.totalSessions,
  'total_favorites': instance.totalFavorites,
  'total_wrong_questions': instance.totalWrongQuestions,
  'consecutive_days': instance.consecutiveDays,
  'total_practice_days': instance.totalPracticeDays,
};

BankStatisticsModel _$BankStatisticsModelFromJson(Map<String, dynamic> json) =>
    BankStatisticsModel(
      bankId: json['bank_id'] as String,
      bankName: json['bank_name'] as String?,
      totalQuestions: (json['total_questions'] as num).toInt(),
      practicedQuestions: (json['practiced_questions'] as num).toInt(),
      correctCount: (json['correct_count'] as num).toInt(),
      wrongCount: (json['wrong_count'] as num).toInt(),
      accuracyRate: (json['accuracy_rate'] as num).toDouble(),
      favoriteCount: (json['favorite_count'] as num).toInt(),
      wrongQuestionsCount: (json['wrong_questions_count'] as num).toInt(),
      totalTimeSpent: (json['total_time_spent'] as num).toInt(),
    );

Map<String, dynamic> _$BankStatisticsModelToJson(
  BankStatisticsModel instance,
) => <String, dynamic>{
  'bank_id': instance.bankId,
  'bank_name': instance.bankName,
  'total_questions': instance.totalQuestions,
  'practiced_questions': instance.practicedQuestions,
  'correct_count': instance.correctCount,
  'wrong_count': instance.wrongCount,
  'accuracy_rate': instance.accuracyRate,
  'favorite_count': instance.favoriteCount,
  'wrong_questions_count': instance.wrongQuestionsCount,
  'total_time_spent': instance.totalTimeSpent,
};

DailyStatisticsModel _$DailyStatisticsModelFromJson(
  Map<String, dynamic> json,
) => DailyStatisticsModel(
  date: json['date'] as String,
  questionsPracticed: (json['questions_practiced'] as num).toInt(),
  correctCount: (json['correct_count'] as num).toInt(),
  wrongCount: (json['wrong_count'] as num).toInt(),
  accuracyRate: (json['accuracy_rate'] as num).toDouble(),
  timeSpent: (json['time_spent'] as num).toInt(),
  sessionsCount: (json['sessions_count'] as num).toInt(),
);

Map<String, dynamic> _$DailyStatisticsModelToJson(
  DailyStatisticsModel instance,
) => <String, dynamic>{
  'date': instance.date,
  'questions_practiced': instance.questionsPracticed,
  'correct_count': instance.correctCount,
  'wrong_count': instance.wrongCount,
  'accuracy_rate': instance.accuracyRate,
  'time_spent': instance.timeSpent,
  'sessions_count': instance.sessionsCount,
};

StatisticsOverviewResponse _$StatisticsOverviewResponseFromJson(
  Map<String, dynamic> json,
) => StatisticsOverviewResponse(
  statistics: StatisticsOverviewModel.fromJson(
    json['statistics'] as Map<String, dynamic>,
  ),
);

Map<String, dynamic> _$StatisticsOverviewResponseToJson(
  StatisticsOverviewResponse instance,
) => <String, dynamic>{'statistics': instance.statistics};

BankStatisticsListResponse _$BankStatisticsListResponseFromJson(
  Map<String, dynamic> json,
) => BankStatisticsListResponse(
  bankStats: (json['bank_stats'] as List<dynamic>)
      .map((e) => BankStatisticsModel.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$BankStatisticsListResponseToJson(
  BankStatisticsListResponse instance,
) => <String, dynamic>{'bank_stats': instance.bankStats};

DailyStatisticsListResponse _$DailyStatisticsListResponseFromJson(
  Map<String, dynamic> json,
) => DailyStatisticsListResponse(
  dailyStats: (json['daily_stats'] as List<dynamic>)
      .map((e) => DailyStatisticsModel.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$DailyStatisticsListResponseToJson(
  DailyStatisticsListResponse instance,
) => <String, dynamic>{'daily_stats': instance.dailyStats};
