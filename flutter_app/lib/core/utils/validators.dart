import '../constants/app_constants.dart';

/// Validators
/// 表单验证工具类
class Validators {
  /// 验证邮箱
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入邮箱';
    }
    if (!AppConstants.emailRegex.hasMatch(value)) {
      return '请输入有效的邮箱地址';
    }
    return null;
  }

  /// 验证用户名
  static String? validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入用户名';
    }
    if (value.length < 3) {
      return '用户名至少3个字符';
    }
    if (value.length > 20) {
      return '用户名最多20个字符';
    }
    if (!AppConstants.usernameRegex.hasMatch(value)) {
      return '用户名只能包含字母、数字和下划线';
    }
    return null;
  }

  /// 验证密码
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入密码';
    }
    if (value.length < 6) {
      return '密码至少6个字符';
    }
    if (!AppConstants.passwordRegex.hasMatch(value)) {
      return '密码必须包含字母和数字';
    }
    return null;
  }

  /// 验证确认密码
  static String? validateConfirmPassword(String? value, String? password) {
    if (value == null || value.isEmpty) {
      return '请确认密码';
    }
    if (value != password) {
      return '两次输入的密码不一致';
    }
    return null;
  }

  /// 验证非空
  static String? validateRequired(String? value, [String? fieldName]) {
    if (value == null || value.isEmpty) {
      return '${fieldName ?? '此字段'}不能为空';
    }
    return null;
  }

  /// 验证手机号
  static String? validatePhone(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入手机号';
    }
    final phoneRegex = RegExp(r'^1[3-9]\d{9}$');
    if (!phoneRegex.hasMatch(value)) {
      return '请输入有效的手机号';
    }
    return null;
  }

  /// 验证激活码
  static String? validateActivationCode(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入激活码';
    }
    if (value.length < 6) {
      return '激活码格式不正确';
    }
    return null;
  }

  /// 验证数字
  static String? validateNumber(String? value, [String? fieldName]) {
    if (value == null || value.isEmpty) {
      return '${fieldName ?? '此字段'}不能为空';
    }
    if (int.tryParse(value) == null) {
      return '请输入有效的数字';
    }
    return null;
  }

  /// 验证数字范围
  static String? validateNumberRange(
    String? value,
    int min,
    int max, [
    String? fieldName,
  ]) {
    final error = validateNumber(value, fieldName);
    if (error != null) return error;

    final number = int.parse(value!);
    if (number < min || number > max) {
      return '${fieldName ?? '数值'}必须在$min到$max之间';
    }
    return null;
  }

  /// 验证长度
  static String? validateLength(
    String? value,
    int min,
    int max, [
    String? fieldName,
  ]) {
    if (value == null || value.isEmpty) {
      return '${fieldName ?? '此字段'}不能为空';
    }
    if (value.length < min) {
      return '${fieldName ?? '此字段'}至少$min个字符';
    }
    if (value.length > max) {
      return '${fieldName ?? '此字段'}最多$max个字符';
    }
    return null;
  }
}
