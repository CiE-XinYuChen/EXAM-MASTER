package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExamModeScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    var showTimeDialog by remember { mutableStateOf(false) }
    var showQuestionDialog by remember { mutableStateOf(false) }
    var selectedExamType by remember { mutableStateOf<ExamType?>(null) }
    
    // 检查是否有未完成的考试
    val currentExamSession by viewModel.currentExamSession.collectAsState()
    val unfinishedExamSession by viewModel.unfinishedExamSession.collectAsState(initial = null)
    var showResumeExamDialog by remember { mutableStateOf(false) }
    
    // 检查未完成的考试
    LaunchedEffect(Unit) {
        viewModel.checkUnfinishedExam()
    }
    
    // 如果有未完成的考试，显示对话框
    LaunchedEffect(unfinishedExamSession) {
        if (unfinishedExamSession != null) {
            showResumeExamDialog = true
        }
    }
    
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
                text = "考试模式",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.width(48.dp))
        }
        
        // 如果有未完成的考试，显示继续考试按钮
        if (unfinishedExamSession != null) {
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = { showResumeExamDialog = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.Restore, contentDescription = "继续考试")
                Spacer(modifier = Modifier.width(8.dp))
                Text("继续未完成的考试")
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Description Card
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Timer,
                    contentDescription = "考试",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(48.dp)
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "考试模式",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "在限定时间内完成考试，系统会自动评分并显示详细的考试结果",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Exam Mode Options
        Column(
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ExamModeCard(
                title = "限时考试",
                subtitle = "设定考试时间和题目数量",
                icon = Icons.Default.Timer,
                onClick = {
                    selectedExamType = ExamType.TIMED
                    showTimeDialog = true
                }
            )
            
            ExamModeCard(
                title = "模拟考试",
                subtitle = "完整的模拟考试体验",
                icon = Icons.Default.Assessment,
                onClick = {
                    selectedExamType = ExamType.SIMULATION
                    showQuestionDialog = true
                }
            )
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Recent Exam Sessions
        Text(
            text = "最近考试记录",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        RecentExamSessions(
            navController = navController,
            viewModel = viewModel
        )
    }
    
    // Time Setting Dialog
    if (showTimeDialog) {
        ExamTimeDialog(
            onDismiss = { showTimeDialog = false },
            onConfirm = { duration, questionCount ->
                showTimeDialog = false
                viewModel.startExam(
                    examType = selectedExamType ?: ExamType.TIMED,
                    duration = duration,
                    questionCount = questionCount
                )
                navController.navigate("exam_question")
            }
        )
    }
    
    // Question Count Dialog
    if (showQuestionDialog) {
        QuestionCountDialog(
            onDismiss = { showQuestionDialog = false },
            onConfirm = { questionCount ->
                showQuestionDialog = false
                viewModel.startExam(
                    examType = selectedExamType ?: ExamType.SIMULATION,
                    duration = 60 * 60, // 1 hour default
                    questionCount = questionCount
                )
                navController.navigate("exam_question")
            }
        )
    }
    
    // 继续考试对话框
    if (showResumeExamDialog) {
        unfinishedExamSession?.let { session ->
            val questionIds = try {
                val type = object : com.google.gson.reflect.TypeToken<List<String>>() {}.type
                com.google.gson.Gson().fromJson<List<String>>(session.questionIds, type) ?: emptyList()
            } catch (e: Exception) {
                emptyList()
            }
            
            val totalQuestions = questionIds.size
            val startTime = session.startTime.toLongOrNull() ?: 0L
            val currentTime = System.currentTimeMillis()
            val elapsedSeconds = (currentTime - startTime) / 1000
            val remainingSeconds = session.duration - elapsedSeconds
            
            AlertDialog(
                onDismissRequest = { showResumeExamDialog = false },
                title = { Text("继续考试") },
                text = {
                    Column {
                        Text("您有一个未完成的考试")
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "考试类型: ${session.mode}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "题目数量: $totalQuestions",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "剩余时间: ${formatDuration(remainingSeconds.toInt())}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showResumeExamDialog = false
                            viewModel.resumeExam(session.id)
                            navController.navigate("exam_question")
                        }
                    ) {
                        Text("继续考试")
                    }
                },
                dismissButton = {
                    TextButton(
                        onClick = { 
                            showResumeExamDialog = false
                            viewModel.abandonExam(session.id)
                        }
                    ) {
                        Text("放弃考试")
                    }
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExamModeCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(32.dp)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    fontSize = 18.sp,
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
                contentDescription = "进入",
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExamTimeDialog(
    onDismiss: () -> Unit,
    onConfirm: (Int, Int) -> Unit
) {
    var selectedDuration by remember { mutableStateOf(30) } // minutes
    var selectedQuestionCount by remember { mutableStateOf(20) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("设置考试参数") },
        text = {
            Column {
                Text("考试时长 (分钟)")
                Slider(
                    value = selectedDuration.toFloat(),
                    onValueChange = { selectedDuration = it.toInt() },
                    valueRange = 10f..120f,
                    steps = 21
                )
                Text("$selectedDuration 分钟")
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text("题目数量")
                Slider(
                    value = selectedQuestionCount.toFloat(),
                    onValueChange = { selectedQuestionCount = it.toInt() },
                    valueRange = 5f..100f,
                    steps = 18
                )
                Text("$selectedQuestionCount 题")
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(selectedDuration * 60, selectedQuestionCount) }
            ) {
                Text("开始考试")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun QuestionCountDialog(
    onDismiss: () -> Unit,
    onConfirm: (Int) -> Unit
) {
    var selectedQuestionCount by remember { mutableStateOf(50) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("设置题目数量") },
        text = {
            Column {
                Text("题目数量")
                Slider(
                    value = selectedQuestionCount.toFloat(),
                    onValueChange = { selectedQuestionCount = it.toInt() },
                    valueRange = 10f..100f,
                    steps = 17
                )
                Text("$selectedQuestionCount 题")
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(selectedQuestionCount) }
            ) {
                Text("开始模拟考试")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ResumeExamDialog(
    examSession: com.exammaster.data.database.entities.ExamSession,
    onDismiss: () -> Unit,
    onResume: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("继续未完成的考试") },
        text = {
            Column {
                Text("您有一个未完成的考试，是否继续？")
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "考试模式: ${examSession.mode}",
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "开始时间: ${examSession.startTime}",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // 计算剩余时间
                val startTimeMs = examSession.startTime.toLongOrNull() ?: System.currentTimeMillis()
                val durationMs = examSession.duration * 1000L
                val endTimeMs = startTimeMs + durationMs
                val remainingTime = endTimeMs - System.currentTimeMillis()
                val minutes = (remainingTime / 1000) / 60
                val seconds = (remainingTime / 1000) % 60
                
                Text(
                    text = "剩余时间: ${String.format("%02d:%02d", minutes, seconds)}",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = onResume
            ) {
                Text("继续考试")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}

@Composable
private fun RecentExamSessions(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val recentExams by viewModel.recentExamSessions.collectAsState()
    
    if (recentExams.isEmpty()) {
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.HistoryEdu,
                    contentDescription = "暂无记录",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(48.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "暂无考试记录",
                    fontSize = 16.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    } else {
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            recentExams.take(3).forEach { examSession ->
                ExamSessionCard(
                    examSession = examSession,
                    onClick = {
                        navController.navigate("exam_result/${examSession.id}")
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExamSessionCard(
    examSession: com.exammaster.data.database.entities.ExamSession,
    onClick: () -> Unit
) {
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
            Icon(
                imageVector = if (examSession.completed) Icons.Default.CheckCircle else Icons.Default.Schedule,
                contentDescription = if (examSession.completed) "已完成" else "进行中",
                tint = if (examSession.completed) 
                    MaterialTheme.colorScheme.primary 
                else 
                    MaterialTheme.colorScheme.error
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = examSession.mode,
                    fontWeight = FontWeight.Medium
                )
                
                // 显示考试日期时间
                Text(
                    text = "时间: ${formatStartTime(examSession.startTime)}",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // 显示考试时长
                Text(
                    text = "时长: ${formatDuration(examSession.duration)}",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // 显示题目数量
                val questionCount = remember(examSession.questionIds) {
                    try {
                        val type = object : com.google.gson.reflect.TypeToken<List<String>>() {}.type
                        val questionIds = com.google.gson.Gson().fromJson<List<String>>(examSession.questionIds, type) ?: emptyList()
                        questionIds.size
                    } catch (e: Exception) {
                        -1
                    }
                }
                
                Text(
                    text = "题目: ${if (questionCount >= 0) "${questionCount}题" else "未知"}",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            if (examSession.completed && examSession.score != null) {
                Text(
                    text = "${(examSession.score * 100).toInt()}分",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

enum class ExamType {
    TIMED, SIMULATION
}

@Composable
private fun formatDuration(seconds: Int): String {
    val hours = seconds / 3600
    val minutes = (seconds % 3600) / 60
    val remainingSeconds = seconds % 60
    
    return if (hours > 0) {
        String.format("%d小时%02d分%02d秒", hours, minutes, remainingSeconds)
    } else {
        String.format("%02d分%02d秒", minutes, remainingSeconds)
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
