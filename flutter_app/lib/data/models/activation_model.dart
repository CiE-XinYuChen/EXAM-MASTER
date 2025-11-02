import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'activation_model.g.dart';

/// Activation Access Model
/// 用户题库访问权限模型
@JsonSerializable()
class ActivationAccessModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'bank_id')
  final String bankId;
  @JsonKey(name: 'bank_name')
  final String? bankName;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'is_permanent')
  final bool isPermanent;
  @JsonKey(name: 'expire_at')
  final String? expireAt;
  @JsonKey(name: 'activated_at')
  final String activatedAt;
  @JsonKey(name: 'is_expired')
  final bool? isExpired;

  const ActivationAccessModel({
    required this.id,
    required this.userId,
    required this.bankId,
    this.bankName,
    required this.isActive,
    required this.isPermanent,
    this.expireAt,
    required this.activatedAt,
    this.isExpired,
  });

  factory ActivationAccessModel.fromJson(Map<String, dynamic> json) =>
      _$ActivationAccessModelFromJson(json);

  Map<String, dynamic> toJson() => _$ActivationAccessModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        bankId,
        bankName,
        isActive,
        isPermanent,
        expireAt,
        activatedAt,
        isExpired,
      ];

  /// Check if access is valid
  bool get isValid => isActive && (isPermanent || !(isExpired ?? true));

  /// Get remaining days
  int? get remainingDays {
    if (isPermanent || expireAt == null) return null;
    final expire = DateTime.parse(expireAt!);
    final now = DateTime.now();
    return expire.difference(now).inDays;
  }
}

/// Activate Code Request
@JsonSerializable()
class ActivateCodeRequest {
  final String code;

  const ActivateCodeRequest({
    required this.code,
  });

  Map<String, dynamic> toJson() => _$ActivateCodeRequestToJson(this);
}

/// Activate Code Response
@JsonSerializable()
class ActivateCodeResponse extends Equatable {
  final bool success;
  final String? message;
  @JsonKey(name: 'bank_id')
  final String? bankId;
  @JsonKey(name: 'bank_name')
  final String? bankName;
  @JsonKey(name: 'is_permanent')
  final bool? isPermanent;
  @JsonKey(name: 'expire_at')
  final String? expireAt;

  const ActivateCodeResponse({
    required this.success,
    this.message,
    this.bankId,
    this.bankName,
    this.isPermanent,
    this.expireAt,
  });

  factory ActivateCodeResponse.fromJson(Map<String, dynamic> json) =>
      _$ActivateCodeResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ActivateCodeResponseToJson(this);

  @override
  List<Object?> get props => [
        success,
        message,
        bankId,
        bankName,
        isPermanent,
        expireAt,
      ];
}

/// My Access List Response
@JsonSerializable()
class MyAccessListResponse extends Equatable {
  final List<ActivationAccessModel> access;
  final int total;

  const MyAccessListResponse({
    required this.access,
    required this.total,
  });

  factory MyAccessListResponse.fromJson(Map<String, dynamic> json) =>
      _$MyAccessListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$MyAccessListResponseToJson(this);

  @override
  List<Object?> get props => [access, total];
}
