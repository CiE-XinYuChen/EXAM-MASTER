import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../providers/auth_provider.dart';

/// Splash Screen
/// 启动页面 - 检查认证状态并自动导航
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuthAndNavigate();
  }

  Future<void> _checkAuthAndNavigate() async {
    // Wait for auth state to initialize
    await Future.delayed(const Duration(milliseconds: 1500));

    if (!mounted) return;

    final authProvider = context.read<AuthProvider>();

    // Navigate based on auth state
    if (authProvider.isAuthenticated) {
      Navigator.of(context).pushReplacementNamed('/home');
    } else {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).primaryColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            const Icon(
              Icons.school_rounded,
              size: 120,
              color: Colors.white,
            ),
            const SizedBox(height: 24),

            // App Name
            const Text(
              'EXAM MASTER',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 8),

            // Subtitle
            const Text(
              '智能刷题系统',
              style: TextStyle(
                fontSize: 18,
                color: Colors.white70,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 48),

            // Loading Indicator
            SpinKitFadingCircle(
              color: Colors.white,
              size: 50.0,
            ),
          ],
        ),
      ),
    );
  }
}
