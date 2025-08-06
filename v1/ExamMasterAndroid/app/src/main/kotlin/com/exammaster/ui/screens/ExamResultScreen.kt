package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExamResultScreen(
    navController: NavController,
    viewModel: ExamViewModel,
    examSessionId: String
) {
    val examResult by viewModel.getExamResult(examSessionId.toIntOrNull() ?: 0).collectAsState(initial = null)
    val isLoading by viewModel.isLoading.collectAsState()
    
    LaunchedEffect(examSessionId) {
        viewModel.loadExamResult(examSessionId.toIntOrNull() ?: 0)
    }
    
    if (isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
        return
    }
    
    examResult?.let { result ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Top Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { navController.popBackStack() }) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                }
                
                Text(
                    text = if (result.completed) "考试结果" else "未完成的考试",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                
                if (result.completed) {
                    IconButton(
                        onClick = { viewModel.shareExamResult(result) }
                    ) {
                        Icon(Icons.Default.Share, contentDescription = "分享")
                    }
                } else {
                    // 显示继续考试按钮
                    IconButton(
                        onClick = { 
                            viewModel.resumeExam(result.examSessionId)
                            navController.navigate("exam_question")
                        }
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = "继续考试")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            if (!result.completed) {
                // 显示未完成考试的信息卡片
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "未完成考试",
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(48.dp)
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = "考试尚未完成",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center
                        )
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            text = "您可以选择继续完成这次考试或放弃考试",
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center
                        )
                        
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            OutlinedButton(
                                onClick = { 
                                    viewModel.abandonExam(result.examSessionId) 
                                    navController.popBackStack()
                                }
                            ) {
                                Text("放弃考试")
                            }
                            
                            Button(
                                onClick = { 
                                    viewModel.resumeExam(result.examSessionId)
                                    navController.navigate("exam_question")
                                }
                            ) {
                                Text("继续考试")
                            }
                        }
                    }
                }
            } else {
                // 已完成考试才显示分数和统计信息
                // Score Card
                ScoreCard(result = result)
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Statistics Cards
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        modifier = Modifier.weight(1f),
                        title = "用时",
                        value = formatDuration(result.duration),
                        icon = Icons.Default.Timer
                    )
                    
                    StatCard(
                        modifier = Modifier.weight(1f),
                        title = "正确率",
                        value = "${(result.accuracy * 100).roundToInt()}%",
                        icon = Icons.Default.CheckCircle
                    )
                }
            }
            
            if (result.completed) {
                Spacer(modifier = Modifier.height(12.dp))
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        modifier = Modifier.weight(1f),
                        title = "正确题数",
                        value = "${result.correctAnswers}",
                        icon = Icons.Default.Done
                    )
                    
                    StatCard(
                        modifier = Modifier.weight(1f),
                        title = "错误题数",
                        value = "${result.totalQuestions - result.correctAnswers}",
                        icon = Icons.Default.Close
                    )
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = { 
                            viewModel.reviewWrongAnswers(result.examSessionId)
                            navController.navigate("question_practice")
                        },
                        modifier = Modifier.weight(1f),
                        enabled = result.correctAnswers < result.totalQuestions
                    ) {
                        Icon(Icons.Default.ErrorOutline, contentDescription = "错题回顾")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("错题回顾")
                    }
                    
                    Button(
                        onClick = { 
                            navController.navigate("exam_mode") {
                                popUpTo("exam_mode") { inclusive = true }
                            }
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Refresh, contentDescription = "再次考试")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("再次考试")
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Detailed Results
                Text(
                    text = "答题详情",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                DetailedResultsList(
                    answers = result.answers,
                    onQuestionClick = { questionId ->
                        viewModel.loadQuestionById(questionId)
                        navController.navigate("question")
                    }
                )
            } else {
                // 未完成考试不显示详情
                Spacer(modifier = Modifier.height(24.dp))
                
                // 考试基本信息
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            text = "考试信息",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Text(
                            text = "开始时间: ${formatStartTime(result.startTime)}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        
                        Text(
                            text = "题目总数: ${result.totalQuestions}道",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        
                        Text(
                            text = "已答题数: ${result.answers.size}道",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    } ?: run {
        // Error state
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Error,
                contentDescription = "错误",
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.error
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "无法加载考试结果",
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Button(onClick = { navController.popBackStack() }) {
                Text("返回")
            }
        }
    }
}

@Composable
private fun ScoreCard(result: ExamViewModel.ExamResult) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = getScoreColor(result.score)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "考试得分",
                fontSize = 16.sp,
                color = Color.White
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "${(result.score * 100).roundToInt()}",
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            
            Text(
                text = "分",
                fontSize = 20.sp,
                color = Color.White
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = getScoreGrade(result.score),
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White
            )
        }
    }
}

@Composable
private fun StatCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector
) {
    Card(
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = value,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            
            Text(
                text = title,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun DetailedResultsList(
    answers: List<ExamViewModel.ExamAnswer>,
    onQuestionClick: (String) -> Unit
) {
    LazyColumn(
        modifier = Modifier.heightIn(max = 400.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(answers) { answer ->
            ExamAnswerCard(
                answer = answer,
                onClick = { onQuestionClick(answer.questionId) }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExamAnswerCard(
    answer: ExamViewModel.ExamAnswer,
    onClick: () -> Unit
) {
    // 判断题答案转换
    val isJudgmentQuestion = answer.questionType == "判断题"
    val displayUserAnswer = if (isJudgmentQuestion) {
        when (answer.userAnswer) {
            "A" -> "正确"
            "B" -> "错误"
            else -> "未作答"
        }
    } else {
        answer.userAnswer.ifEmpty { "未作答" }
    }
    
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Result Icon
            Icon(
                imageVector = if (answer.isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                contentDescription = if (answer.isCorrect) "正确" else "错误",
                tint = if (answer.isCorrect) 
                    MaterialTheme.colorScheme.primary 
                else 
                    MaterialTheme.colorScheme.error,
                modifier = Modifier.size(24.dp)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "题目 ${answer.questionId}",
                    fontWeight = FontWeight.Medium
                )
                
                Row {
                    Text(
                        text = "您的答案: $displayUserAnswer",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    
                    if (!answer.isCorrect) {
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "正确答案: ${answer.correctAnswer}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.primary
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

private fun getScoreColor(score: Float): Color {
    return when {
        score >= 0.9f -> Color(0xFF4CAF50) // Green
        score >= 0.8f -> Color(0xFF8BC34A) // Light Green
        score >= 0.7f -> Color(0xFFFFC107) // Yellow
        score >= 0.6f -> Color(0xFFFF9800) // Orange
        else -> Color(0xFFF44336) // Red
    }
}

private fun getScoreGrade(score: Float): String {
    return when {
        score >= 0.95f -> "优秀+"
        score >= 0.9f -> "优秀"
        score >= 0.85f -> "良好+"
        score >= 0.8f -> "良好"
        score >= 0.75f -> "中等+"
        score >= 0.7f -> "中等"
        score >= 0.6f -> "及格"
        else -> "不及格"
    }
}

private fun formatDuration(seconds: Int): String {
    val hours = seconds / 3600
    val minutes = (seconds % 3600) / 60
    val secs = seconds % 60
    
    return when {
        hours > 0 -> String.format("%d:%02d:%02d", hours, minutes, secs)
        else -> String.format("%02d:%02d", minutes, secs)
    }
}

private fun formatStartTime(timestamp: String): String {
    val time = timestamp.toLongOrNull() ?: return "未知时间"
    return try {
        val date = java.util.Date(time)
        val format = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.getDefault())
        format.format(date)
    } catch (e: Exception) {
        "未知时间"
    }
}
