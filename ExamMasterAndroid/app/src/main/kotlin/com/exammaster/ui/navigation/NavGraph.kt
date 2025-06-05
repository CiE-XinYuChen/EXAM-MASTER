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
    viewModel: ExamViewModel
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route
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
}