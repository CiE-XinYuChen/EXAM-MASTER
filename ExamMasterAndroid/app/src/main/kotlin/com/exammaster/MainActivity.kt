package com.exammaster

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.lifecycle.lifecycleScope
import com.exammaster.data.models.AppIcon
import com.exammaster.data.datastore.dataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.exammaster.data.QuestionDataLoader
import com.exammaster.data.database.ExamDatabase
import com.exammaster.data.repository.ExamRepository
import com.exammaster.ui.navigation.NavGraph
import com.exammaster.ui.navigation.Screen
import com.exammaster.ui.screens.*
import com.exammaster.ui.settings.SettingsScreen
import com.exammaster.ui.theme.ExamMasterTheme
import com.exammaster.ui.viewmodel.ExamViewModel
import com.exammaster.ui.viewmodel.ViewModelFactory
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class MainActivity : ComponentActivity() {    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize database and repository
        val database = ExamDatabase.getDatabase(this)
        val repository = ExamRepository(
            database.questionDao(),
            database.historyDao(),
            database.favoriteDao(),
            database.examSessionDao()
        )
          
        // 检查并初始化图标 - 这应该在setContent之前进行
        initializeAppIcon()
          
        setContent {
            ExamMasterTheme {
                val viewModelFactory = ViewModelFactory(repository)
                val viewModel: ExamViewModel = viewModel(factory = viewModelFactory)
                
                // Initialize data on first launch
                LaunchedEffect(Unit) {
                    val questionCount = repository.getQuestionCount()
                    if (questionCount == 0) {
                        // Load questions from CSV file
                        val questions = QuestionDataLoader.loadQuestionsFromAssets(this@MainActivity)
                        if (questions.isNotEmpty()) {
                            repository.insertQuestions(questions)
                        } else {
                            // Fallback to default questions
                            repository.insertQuestions(QuestionDataLoader.getDefaultQuestions())
                        }
                    }
                }
                
                ExamMasterApp(viewModel)
            }
        }
    }
}

/**
 * 初始化应用图标
 * 从持久化存储中读取用户选择的图标并应用
 */
private fun MainActivity.initializeAppIcon() {
    this.lifecycleScope.launch {
        try {
            // 从统一定义的datastore获取当前应用图标设置
            val preferences = this@initializeAppIcon.dataStore.data.first()
            val appIconStr = preferences[stringPreferencesKey("app_icon")]
            
            // 如果有存储的图标设置，则应用它
            if (!appIconStr.isNullOrEmpty()) {
                val appIcon = AppIcon.valueOf(appIconStr)
                if (appIcon != AppIcon.DEFAULT) {
                    // 确保应用程序已正确初始化
                    val app = applicationContext as ExamMasterApplication
                    app.changeAppIcon(appIcon)
                }
            }
        } catch (e: Exception) {
            // 如果出现错误，默认使用默认图标
            e.printStackTrace()
        }
    }
}

// 删除这里的dataStore定义，改用统一的DataStoreInstance.kt定义
// 避免多个DataStore实例的问题

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExamMasterApp(viewModel: ExamViewModel) {
    val navController = rememberNavController()
    
    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                  val items = listOf(
                    Screen.Home,
                    Screen.History,
                    Screen.Favorites,
                    Screen.Statistics,
                    Screen.Settings
                )
                
                items.forEach { screen ->
                    NavigationBarItem(                        icon = {
                            Icon(
                                when (screen) {
                                    Screen.Home -> Icons.Default.Home
                                    Screen.History -> Icons.Default.History
                                    Screen.Favorites -> Icons.Default.Favorite
                                    Screen.Statistics -> Icons.Default.BarChart
                                    Screen.Settings -> Icons.Default.Settings
                                    else -> Icons.Default.Home
                                },
                                contentDescription = screen.title
                            )
                        },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {            composable(Screen.Home.route) {
                HomeScreen(navController, viewModel)
            }
            composable(Screen.Question.route) {
                QuestionScreen(navController, viewModel)
            }
            composable("practice") {
                PracticeScreen(navController, viewModel)
            }
            composable("exam_mode") {
                ExamModeScreen(navController, viewModel)
            }
            composable("question_practice") {
                QuestionPracticeScreen(navController, viewModel)
            }
            composable("exam_question") {
                ExamQuestionScreen(navController, viewModel)
            }
            composable("exam_result/{examSessionId}") { backStackEntry ->
                val examSessionId = backStackEntry.arguments?.getString("examSessionId") ?: "0"
                ExamResultScreen(navController, viewModel, examSessionId)
            }
            composable(Screen.History.route) {
                HistoryScreen(navController, viewModel)
            }
            composable(Screen.Favorites.route) {
                FavoritesScreen(navController, viewModel)
            }
            composable(Screen.Statistics.route) {
                StatisticsScreen(navController, viewModel)
            }
            composable(Screen.Search.route) {
                SearchScreen(navController, viewModel)
            }
            composable(Screen.Browse.route) {
                BrowseScreen(navController, viewModel)
            }
            composable(Screen.About.route) {
                AboutScreen(navController, viewModel)
            }
            composable(Screen.Settings.route) {
                SettingsScreen(navController)
            }
        }
    }
}