import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/utils/validators.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_text_field.dart';
import '../../widgets/common/loading_button.dart';

/// Register Screen
/// 注册页面
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Check password confirmation
    if (_passwordController.text != _confirmPasswordController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('两次输入的密码不一致'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.register(
      username: _usernameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text,
      confirmPassword: _confirmPasswordController.text,
    );

    if (!mounted) return;

    if (success) {
      // Navigate to home screen
      Navigator.of(context).pushReplacementNamed('/home');
    } else {
      // Show error message
      if (authProvider.errorMessage != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage!),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _navigateToLogin() {
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('注册'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: _navigateToLogin,
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Header
                  Icon(
                    Icons.person_add_rounded,
                    size: 80,
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '创建账号',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).primaryColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '注册并开始学习之旅',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Username Field
                  CustomTextField(
                    controller: _usernameController,
                    labelText: '用户名',
                    hintText: '请输入用户名',
                    prefixIcon: Icons.person_outline,
                    validator: Validators.validateUsername,
                  ),
                  const SizedBox(height: 16),

                  // Email Field
                  CustomTextField(
                    controller: _emailController,
                    labelText: '邮箱',
                    hintText: '请输入邮箱地址',
                    prefixIcon: Icons.email_outlined,
                    keyboardType: TextInputType.emailAddress,
                    validator: Validators.validateEmail,
                  ),
                  const SizedBox(height: 16),

                  // Password Field
                  CustomTextField(
                    controller: _passwordController,
                    labelText: '密码',
                    hintText: '请输入密码（至少6个字符）',
                    prefixIcon: Icons.lock_outline,
                    obscureText: _obscurePassword,
                    validator: Validators.validatePassword,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_off
                            : Icons.visibility,
                      ),
                      onPressed: () {
                        setState(() {
                          _obscurePassword = !_obscurePassword;
                        });
                      },
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Confirm Password Field
                  CustomTextField(
                    controller: _confirmPasswordController,
                    labelText: '确认密码',
                    hintText: '请再次输入密码',
                    prefixIcon: Icons.lock_outline,
                    obscureText: _obscureConfirmPassword,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请再次输入密码';
                      }
                      if (value != _passwordController.text) {
                        return '两次输入的密码不一致';
                      }
                      return null;
                    },
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPassword
                            ? Icons.visibility_off
                            : Icons.visibility,
                      ),
                      onPressed: () {
                        setState(() {
                          _obscureConfirmPassword = !_obscureConfirmPassword;
                        });
                      },
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Register Button
                  Consumer<AuthProvider>(
                    builder: (context, authProvider, child) {
                      return LoadingButton(
                        text: '注册',
                        isLoading: authProvider.isLoading,
                        onPressed: _handleRegister,
                      );
                    },
                  ),
                  const SizedBox(height: 16),

                  // Login Link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        '已有账号？',
                        style: TextStyle(color: Colors.grey),
                      ),
                      TextButton(
                        onPressed: _navigateToLogin,
                        child: const Text('立即登录'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
