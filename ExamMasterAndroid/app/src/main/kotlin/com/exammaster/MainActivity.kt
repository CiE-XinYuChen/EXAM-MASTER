package com.exammaster

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
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
import com.exammaster.ui.theme.ExamMasterTheme
import com.exammaster.ui.viewmodel.ExamViewModel
import com.exammaster.ui.viewmodel.ViewModelFactory
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize database and repository
        val database = ExamDatabase.getDatabase(this)
        val repository = ExamRepository(
            database.questionDao(),
            database.historyDao(),
            database.favoriteDao(),
            database.examSessionDao()
        )
        
        setContent {
            ExamMasterTheme {
                val viewModelFactory = ViewModelFactory(repository)
                val viewModel: ExamViewModel = viewModel(factory = viewModelFactory)
                
                // Initialize data on first launch
                LaunchedEffect(Unit) {
                    launch {
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
                }
                
                ExamMasterApp(viewModel)
            }
        }
    }
}

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
                    Screen.About
                )
                
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = {
                            Icon(
                                when (screen) {
                                    Screen.Home -> Icons.Default.Home
                                    Screen.History -> Icons.Default.History
                                    Screen.Favorites -> Icons.Default.Favorite
                                    Screen.Statistics -> Icons.Default.BarChart
                                    Screen.About -> Icons.Default.Info
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
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Home.route) {
                HomeScreen(navController, viewModel)
            }
            composable(Screen.Question.route) {
                QuestionScreen(navController, viewModel)
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
        }
    }
}