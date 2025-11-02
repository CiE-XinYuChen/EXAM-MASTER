import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'question_bank_model.g.dart';

/// Question Bank Model
/// 题库数据模型
@JsonSerializable()
class QuestionBankModel extends Equatable {
  final String id;
  final String name;
  final String? description;
  final String? category;
  final List<String>? tags;
  @JsonKey(name: 'is_public')
  final bool? isPublic;
  @JsonKey(name: 'total_questions')
  final int? totalQuestions;
  @JsonKey(name: 'created_at')
  final String? createdAt;
  @JsonKey(name: 'updated_at')
  final String? updatedAt;

  const QuestionBankModel({
    required this.id,
    required this.name,
    this.description,
    this.category,
    this.tags,
    this.isPublic,
    this.totalQuestions,
    this.createdAt,
    this.updatedAt,
  });

  factory QuestionBankModel.fromJson(Map<String, dynamic> json) =>
      _$QuestionBankModelFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionBankModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        category,
        tags,
        isPublic,
        totalQuestions,
        createdAt,
        updatedAt,
      ];

  QuestionBankModel copyWith({
    String? id,
    String? name,
    String? description,
    String? category,
    List<String>? tags,
    bool? isPublic,
    int? totalQuestions,
    String? createdAt,
    String? updatedAt,
  }) {
    return QuestionBankModel(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      isPublic: isPublic ?? this.isPublic,
      totalQuestions: totalQuestions ?? this.totalQuestions,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// Question Bank List Response
@JsonSerializable()
class QuestionBankListResponse extends Equatable {
  final List<QuestionBankModel> banks;
  final int total;

  const QuestionBankListResponse({
    required this.banks,
    required this.total,
  });

  factory QuestionBankListResponse.fromJson(Map<String, dynamic> json) =>
      _$QuestionBankListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$QuestionBankListResponseToJson(this);

  @override
  List<Object?> get props => [banks, total];
}
