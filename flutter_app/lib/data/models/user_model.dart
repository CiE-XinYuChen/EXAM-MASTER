import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'user_model.g.dart';

/// User Model
/// 用户数据模型
@JsonSerializable()
class UserModel extends Equatable {
  final int id;
  final String username;
  final String email;
  @JsonKey(name: 'is_active')
  final bool isActive;
  final String role;
  @JsonKey(name: 'created_at')
  final String? createdAt;
  @JsonKey(name: 'updated_at')
  final String? updatedAt;

  const UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.isActive,
    required this.role,
    this.createdAt,
    this.updatedAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        username,
        email,
        isActive,
        role,
        createdAt,
        updatedAt,
      ];

  UserModel copyWith({
    int? id,
    String? username,
    String? email,
    bool? isActive,
    String? role,
    String? createdAt,
    String? updatedAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      isActive: isActive ?? this.isActive,
      role: role ?? this.role,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// Login Response
@JsonSerializable()
class LoginResponse extends Equatable {
  @JsonKey(name: 'access_token')
  final String accessToken;
  @JsonKey(name: 'token_type')
  final String tokenType;
  final UserModel? user;

  const LoginResponse({
    required this.accessToken,
    required this.tokenType,
    this.user,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) =>
      _$LoginResponseFromJson(json);

  Map<String, dynamic> toJson() => _$LoginResponseToJson(this);

  @override
  List<Object?> get props => [accessToken, tokenType, user];
}

/// Register Request
@JsonSerializable()
class RegisterRequest {
  final String username;
  final String email;
  final String password;
  @JsonKey(name: 'confirm_password')
  final String confirmPassword;

  const RegisterRequest({
    required this.username,
    required this.email,
    required this.password,
    required this.confirmPassword,
  });

  Map<String, dynamic> toJson() => _$RegisterRequestToJson(this);
}

/// Login Request
@JsonSerializable()
class LoginRequest {
  final String username;
  final String password;

  const LoginRequest({
    required this.username,
    required this.password,
  });

  Map<String, dynamic> toJson() => _$LoginRequestToJson(this);
}
