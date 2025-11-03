import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/network/dio_client.dart';
import 'core/storage/local_storage.dart';
import 'core/utils/logger.dart';
import 'core/constants/api_constants.dart';
import 'data/datasources/remote/auth_api.dart';
import 'data/datasources/remote/question_bank_api.dart';
import 'data/datasources/remote/practice_api.dart';
import 'data/datasources/remote/favorites_api.dart';
import 'data/repositories/auth_repository.dart';
import 'data/repositories/question_bank_repository.dart';
import 'data/repositories/practice_repository.dart';
import 'data/repositories/favorites_repository.dart';
import 'presentation/providers/auth_provider.dart';
import 'presentation/providers/question_bank_provider.dart';
import 'presentation/providers/practice_provider.dart';
import 'presentation/screens/splash_screen.dart';
import 'presentation/screens/auth/login_screen.dart';
import 'presentation/screens/auth/register_screen.dart';
import 'presentation/screens/home/main_screen.dart';
import 'presentation/screens/question_bank/question_bank_detail_screen.dart';
import 'presentation/screens/practice/practice_screen.dart';
import 'data/models/practice_session_model.dart';

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
    final questionBankRepository = QuestionBankRepository(
      api: QuestionBankApi(dioClient),
    );
    final practiceRepository = PracticeRepository(
      api: PracticeApi(dioClient),
    );
    final favoritesRepository = FavoritesRepository(
      api: FavoritesApi(dioClient),
    );

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authRepository: authRepository),
        ),
        ChangeNotifierProvider(
          create: (_) => QuestionBankProvider(
            repository: questionBankRepository,
          ),
        ),
        ChangeNotifierProxyProvider<AuthProvider, PracticeProvider>(
          create: (context) => PracticeProvider(
            repository: practiceRepository,
            questionBankRepository: questionBankRepository,
            favoritesRepository: favoritesRepository,
            getUserId: () => context.read<AuthProvider>().currentUser?.id,
          ),
          update: (context, authProvider, previousProvider) => PracticeProvider(
            repository: practiceRepository,
            questionBankRepository: questionBankRepository,
            favoritesRepository: favoritesRepository,
            getUserId: () => authProvider.currentUser?.id,
          ),
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
        onGenerateRoute: (settings) {
          // Handle routes with arguments
          if (settings.name == '/question-bank-detail') {
            final bankId = settings.arguments as String;
            return MaterialPageRoute(
              builder: (context) => QuestionBankDetailScreen(bankId: bankId),
            );
          }

          if (settings.name == '/practice') {
            final args = settings.arguments as Map<String, dynamic>;
            return MaterialPageRoute(
              builder: (context) => PracticeScreen(
                bankId: args['bankId'] as String,
                mode: args['mode'] as PracticeMode,
              ),
            );
          }

          return null;
        },
      ),
    );
  }
}
