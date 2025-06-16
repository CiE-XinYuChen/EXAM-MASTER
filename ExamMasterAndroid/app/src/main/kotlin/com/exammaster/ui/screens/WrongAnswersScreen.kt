package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel
import com.exammaster.data.database.entities.Question

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WrongAnswersScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val wrongQuestions by viewModel.getWrongQuestions().collectAsState(initial = emptyList())
    val statistics by viewModel.statistics.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadStatistics()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("错题记录") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 概览卡片
                item {
                    WrongAnswersOverviewCard(
                        wrongCount = wrongQuestions.size,
                        totalAnswered = statistics.answeredQuestions,
                        accuracy = statistics.accuracy,
                        onPracticeClick = {
                            if (wrongQuestions.isNotEmpty()) {
                                // 预先加载第一道错题以避免闪屏
                                val firstWrongQuestion = wrongQuestions.random()
                                viewModel.loadQuestionById(firstWrongQuestion.id)
                                viewModel.startPracticeMode(ExamViewModel.QuizMode.WRONG_ONLY)
                                navController.navigate("question_practice") {
                                    launchSingleTop = true
                                }
                            }
                        }
                    )
                }

                if (wrongQuestions.isEmpty()) {
                    item {
                        EmptyWrongAnswersState()
                    }
                } else {
                    item {
                        Text(
                            text = "错题列表",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }

                    items(wrongQuestions) { question ->
                        WrongQuestionItem(
                            question = question,
                            viewModel = viewModel,
                            onClick = {
                                // 修复闪屏：同步加载题目再导航
                                viewModel.loadQuestionById(question.id)
                                navController.navigate("question") {
                                    launchSingleTop = true
                                }
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun WrongAnswersOverviewCard(
    wrongCount: Int,
    totalAnswered: Int,
    accuracy: Float,
    onPracticeClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "错题概览",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "共 $wrongCount 道错题",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Icon(
                    imageVector = Icons.Default.ErrorOutline,
                    contentDescription = "错题",
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(40.dp)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                StatisticItem(
                    label = "已答题数",
                    value = totalAnswered.toString(),
                    color = MaterialTheme.colorScheme.primary
                )
                StatisticItem(
                    label = "错题数量",
                    value = wrongCount.toString(),
                    color = MaterialTheme.colorScheme.error
                )
                StatisticItem(
                    label = "正确率",
                    value = "${accuracy.toInt()}%",
                    color = if (accuracy >= 80f) Color(0xFF4CAF50) else MaterialTheme.colorScheme.tertiary
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onPracticeClick,
                modifier = Modifier.fillMaxWidth(),
                enabled = wrongCount > 0,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Icon(
                    imageVector = Icons.Default.School,
                    contentDescription = "练习"
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (wrongCount > 0) "开始错题练习" else "暂无错题")
            }
        }
    }
}

@Composable
private fun StatisticItem(
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun WrongQuestionItem(
    question: Question,
    viewModel: ExamViewModel,
    onClick: () -> Unit
) {
    var attemptCount by remember { mutableStateOf(0) }
    
    LaunchedEffect(question.id) {
        viewModel.getQuestionAttemptCount(question.id).collect { count -> 
            attemptCount = count 
        }
    }
    
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(
                    modifier = Modifier.weight(1f)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Surface(
                                color = MaterialTheme.colorScheme.error,
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                Text(
                                    text = "题目 ${question.id}",
                                    color = Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                )
                            }
                            
                            Spacer(modifier = Modifier.width(8.dp))
                            
                            question.qtype?.let { qtype ->
                                AssistChip(
                                    onClick = { },
                                    label = { Text(qtype, fontSize = 10.sp) },
                                    modifier = Modifier.height(24.dp)
                                )
                            }
                        }
                        
                        // 作答次数标签
                        if (attemptCount > 0) {
                            Surface(
                                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.6f),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Text(
                                    text = "第${attemptCount}次",
                                    fontSize = 10.sp,
                                    color = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = question.stem,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        maxLines = 2
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Row {
                        question.difficulty?.takeIf { it != "无" && it.isNotBlank() }?.let { difficulty ->
                            AssistChip(
                                onClick = { },
                                label = { Text(difficulty, fontSize = 10.sp) },
                                modifier = Modifier.height(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        
                        question.category?.takeIf { it != "未分类" && it.isNotBlank() }?.let { category ->
                            AssistChip(
                                onClick = { },
                                label = { Text(category, fontSize = 10.sp) },
                                modifier = Modifier.height(20.dp)
                            )
                        }
                    }
                }

                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = "查看详情",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EmptyWrongAnswersState() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = "没有错题",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(64.dp)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "太棒了！",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "您还没有答错的题目，继续保持！",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
} 