package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.navigation.Screen
import com.exammaster.ui.viewmodel.ExamViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val statistics by viewModel.statistics.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // App Title
        Text(
            text = "Exam-Master",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 32.dp)
        )
        
        // Statistics Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "学习统计",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    StatisticItem("总题数", statistics.totalQuestions.toString())
                    StatisticItem("已答题", statistics.answeredQuestions.toString())
                    StatisticItem("正确率", "%.1f%%".format(statistics.accuracy))
                }
            }
        }
        
        // Mode Selection Buttons
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {            item {
                ModeButton(
                    title = "练习模式",
                    subtitle = "随机练习、顺序练习、错题本",
                    icon = Icons.Default.School,
                    onClick = {
                        navController.navigate(Screen.Practice.route)
                    }
                )
            }
            
            item {
                ModeButton(
                    title = "考试模式",
                    subtitle = "限时考试、模拟考试",
                    icon = Icons.Default.Timer,
                    onClick = {
                        navController.navigate(Screen.ExamMode.route)
                    }
                )
            }
            
            item {
                ModeButton(
                    title = "浏览题目",
                    subtitle = "查看所有题目内容",
                    icon = Icons.Default.LibraryBooks,
                    onClick = {
                        navController.navigate(Screen.Browse.route)
                    }
                )
            }
              item {
                ModeButton(
                    title = "顺序答题",
                    subtitle = "从上次浏览位置开始顺序答题",
                    icon = Icons.Default.List,
                    onClick = {
                        viewModel.startSequentialFromLastBrowsed()
                        navController.navigate(Screen.QuestionPractice.route)
                    }
                )
            }
              item {
                ModeButton(
                    title = "错题练习",
                    subtitle = "重新练习答错的题目",
                    icon = Icons.Default.Report,
                    onClick = {
                        viewModel.startPracticeMode(ExamViewModel.QuizMode.WRONG_ONLY)
                        navController.navigate(Screen.QuestionPractice.route)
                    }
                )
            }
            
            item {
                ModeButton(
                    title = "收藏题目",
                    subtitle = "查看和练习收藏的题目",
                    icon = Icons.Default.Favorite,
                    onClick = {
                        navController.navigate(Screen.Favorites.route)
                    }
                )
            }
            
            item {
                ModeButton(
                    title = "搜索题目",
                    subtitle = "根据关键词搜索题目",
                    icon = Icons.Default.Search,
                    onClick = {
                        navController.navigate(Screen.Search.route)
                    }
                )
            }
            
            item {
                ModeButton(
                    title = "答题历史",
                    subtitle = "查看答题记录和统计",
                    icon = Icons.Default.History,
                    onClick = {
                        navController.navigate(Screen.History.route)
                    }
                )
            }
        }
    }
}

@Composable
private fun StatisticItem(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ModeButton(
    title: String,
    subtitle: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                modifier = Modifier.size(40.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = subtitle,
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "Go",
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}