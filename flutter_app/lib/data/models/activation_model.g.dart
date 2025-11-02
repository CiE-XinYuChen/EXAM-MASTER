// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'activation_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ActivationAccessModel _$ActivationAccessModelFromJson(
  Map<String, dynamic> json,
) => ActivationAccessModel(
  id: json['id'] as String,
  userId: (json['user_id'] as num).toInt(),
  bankId: json['bank_id'] as String,
  bankName: json['bank_name'] as String?,
  isActive: json['is_active'] as bool,
  isPermanent: json['is_permanent'] as bool,
  expireAt: json['expire_at'] as String?,
  activatedAt: json['activated_at'] as String,
  isExpired: json['is_expired'] as bool?,
);

Map<String, dynamic> _$ActivationAccessModelToJson(
  ActivationAccessModel instance,
) => <String, dynamic>{
  'id': instance.id,
  'user_id': instance.userId,
  'bank_id': instance.bankId,
  'bank_name': instance.bankName,
  'is_active': instance.isActive,
  'is_permanent': instance.isPermanent,
  'expire_at': instance.expireAt,
  'activated_at': instance.activatedAt,
  'is_expired': instance.isExpired,
};

ActivateCodeRequest _$ActivateCodeRequestFromJson(Map<String, dynamic> json) =>
    ActivateCodeRequest(code: json['code'] as String);

Map<String, dynamic> _$ActivateCodeRequestToJson(
  ActivateCodeRequest instance,
) => <String, dynamic>{'code': instance.code};

ActivateCodeResponse _$ActivateCodeResponseFromJson(
  Map<String, dynamic> json,
) => ActivateCodeResponse(
  success: json['success'] as bool,
  message: json['message'] as String?,
  bankId: json['bank_id'] as String?,
  bankName: json['bank_name'] as String?,
  isPermanent: json['is_permanent'] as bool?,
  expireAt: json['expire_at'] as String?,
);

Map<String, dynamic> _$ActivateCodeResponseToJson(
  ActivateCodeResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'message': instance.message,
  'bank_id': instance.bankId,
  'bank_name': instance.bankName,
  'is_permanent': instance.isPermanent,
  'expire_at': instance.expireAt,
};

MyAccessListResponse _$MyAccessListResponseFromJson(
  Map<String, dynamic> json,
) => MyAccessListResponse(
  access: (json['access'] as List<dynamic>)
      .map((e) => ActivationAccessModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$MyAccessListResponseToJson(
  MyAccessListResponse instance,
) => <String, dynamic>{'access': instance.access, 'total': instance.total};
