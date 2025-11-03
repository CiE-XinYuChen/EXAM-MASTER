import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/network/dio_client.dart';
import 'core/storage/local_storage.dart';
import 'core/utils/logger.dart';
import 'core/constants/api_constants.dart';
import 'data/datasources/remote/auth_api.dart';
import 'data/repositories/auth_repository.dart';
import 'presentation/providers/auth_provider.dart';
import 'presentation/screens/splash_screen.dart';
import 'presentation/screens/auth/login_screen.dart';
import 'presentation/screens/auth/register_screen.dart';
import 'presentation/screens/home/main_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize dependencies
  AppLogger.info('Initializing LocalStorage...');
  await LocalStorage.init();
  AppLogger.info('LocalStorage initialized successfully');

  // Log API configuration
  AppLogger.info('API Base URL: ${ApiConstants.apiBaseUrl}');
  AppLogger.info('Environment: ${ApiConstants.useProduction ? "Production" : "Development"}');

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Initialize dependencies
    final dioClient = DioClient();
    final localStorage = LocalStorage();

    // Initialize repositories
    final authRepository = AuthRepository(
      authApi: AuthApi(dioClient),
      localStorage: localStorage,
    );

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authRepository: authRepository),
        ),
      ],
      child: MaterialApp(
        title: 'EXAM MASTER',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF6200EE),
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          appBarTheme: const AppBarTheme(
            centerTitle: true,
            elevation: 0,
          ),
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/login': (context) => const LoginScreen(),
          '/register': (context) => const RegisterScreen(),
          '/home': (context) => const MainScreen(),
        },
      ),
    );
  }
}
