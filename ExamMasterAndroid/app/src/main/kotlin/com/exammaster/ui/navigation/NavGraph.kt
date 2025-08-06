package com.exammaster.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.exammaster.ui.screens.*
import com.exammaster.ui.settings.SettingsScreen
import com.exammaster.ui.viewmodel.ExamViewModel

@Composable
fun NavGraph(
    navController: NavHostController,
    viewModel: ExamViewModel,
    modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Question.route) {
            QuestionScreen(
                navController = navController,
                viewModel = viewModel
            )
        }

        // 添加缺失的练习模式屏幕
        composable(Screen.Practice.route) {
            PracticeScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        // 添加缺失的考试模式屏幕
        composable(Screen.ExamMode.route) {
            ExamModeScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        // 添加缺失的练习答题屏幕
        composable(Screen.QuestionPractice.route) {
            QuestionPracticeScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        // 添加缺失的考试答题屏幕
        composable(Screen.ExamQuestion.route) {
            ExamQuestionScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        // 添加考试结果屏幕
        composable(Screen.ExamResult.route + "/{examSessionId}") { backStackEntry ->
            val examSessionId = backStackEntry.arguments?.getString("examSessionId") ?: "0"
            ExamResultScreen(navController, viewModel, examSessionId)
        }
        
        composable(Screen.History.route) {
            HistoryScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Favorites.route) {
            FavoritesScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Statistics.route) {
            StatisticsScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Search.route) {
            SearchScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Browse.route) {
            BrowseScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
          composable(Screen.About.route) {
            AboutScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                navController = navController
            )
        }
        
        composable("wrong_answers") {
            WrongAnswersScreen(
                navController = navController,
                viewModel = viewModel
            )
        }
    }
}

sealed class Screen(val route: String, val title: String) {
    object Home : Screen("home", "首页")
    object Question : Screen("question", "答题")
    object History : Screen("history", "历史")
    object Favorites : Screen("favorites", "收藏")
    object Statistics : Screen("statistics", "统计")
    object Search : Screen("search", "搜索")
    object Browse : Screen("browse", "浏览")
    object Settings : Screen("settings", "设置")
    object About : Screen("about", "关于")
    
    // 添加新路由
    object Practice : Screen("practice", "练习模式")
    object ExamMode : Screen("exam_mode", "考试模式")
    object QuestionPractice : Screen("question_practice", "练习答题")
    object ExamQuestion : Screen("exam_question", "考试答题")
    object ExamResult : Screen("exam_result", "考试结果")
}