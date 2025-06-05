package com.exammaster.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
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
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExamQuestionScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val currentQuestion by viewModel.currentQuestion.collectAsState()
    val selectedAnswers by viewModel.selectedAnswers.collectAsState()
    val currentExamSession by viewModel.currentExamSession.collectAsState()
    val examProgress by viewModel.examProgress.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    var showExitDialog by remember { mutableStateOf(false) }
    var timeRemaining by remember { mutableStateOf(0) }
    
    // Timer effect
    LaunchedEffect(currentExamSession) {
        currentExamSession?.let { session ->
            val duration = session.duration
            val startTime = session.startTime.toLongOrNull() ?: System.currentTimeMillis()
            
            while (true) {
                val elapsed = (System.currentTimeMillis() - startTime) / 1000
                timeRemaining = (duration - elapsed).toInt()
                
                if (timeRemaining <= 0) {
                    // Time's up - auto submit exam
                    viewModel.submitExam()
                    navController.navigate("exam_result/${session.id}") {
                        popUpTo("exam_mode") { inclusive = false }
                    }
                    break
                }
                
                delay(1000)
            }
        }
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
    
    // 使用动画包装题目内容
    val questionKey = currentQuestion?.id ?: "empty"
    
    AnimatedQuestionContent(
        targetState = questionKey,
        modifier = Modifier.fillMaxSize()
    ) { questionId ->
        if (questionId == "empty") {
            // 无题目状态
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
            return@AnimatedQuestionContent
        }
        
        // 有题目状态
        currentQuestion?.let { question ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp)
            ) {
                // Top Bar with Timer and Progress
                ExamTopBar(
                    timeRemaining = timeRemaining,
                    progress = examProgress,
                    onExitClick = { showExitDialog = true }
                )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Question Info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "题目 ${examProgress.currentIndex + 1} / ${examProgress.totalQuestions}",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Row {
                    question.difficulty?.let { difficulty ->
                        DifficultyChip(difficulty = difficulty)
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    question.category?.let { category ->
                        CategoryChip(category = category)
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Question Stem
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp)
                ) {
                    Text(
                        text = "题目",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Text(
                        text = question.stem,
                        fontSize = 16.sp,
                        lineHeight = 24.sp
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Options
            if (question.getFormattedOptions().isNotEmpty()) {
                Text(
                    text = "选择答案",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    question.getFormattedOptions().forEach { (key, value) ->
                        ExamOptionCard(
                            key = key,
                            value = value,
                            isSelected = selectedAnswers.contains(key),
                            onClick = { viewModel.selectAnswer(key) }
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Navigation Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                OutlinedButton(
                    onClick = { viewModel.previousExamQuestion() },
                    enabled = examProgress.currentIndex > 0
                ) {
                    Icon(Icons.Default.NavigateBefore, contentDescription = "上一题")
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("上一题")
                }
                
                Button(
                    onClick = { 
                        if (examProgress.currentIndex < examProgress.totalQuestions - 1) {
                            viewModel.nextExamQuestion()
                        } else {
                            // Last question - show submit dialog
                            viewModel.showSubmitExamDialog()
                        }
                    }
                ) {
                    Text(
                        if (examProgress.currentIndex < examProgress.totalQuestions - 1) "下一题" else "提交考试"
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(
                        if (examProgress.currentIndex < examProgress.totalQuestions - 1) 
                            Icons.Default.NavigateNext 
                        else 
                            Icons.Default.Send,
                        contentDescription = if (examProgress.currentIndex < examProgress.totalQuestions - 1) "下一题" else "提交"
                    )
                }
            }
        }
    }
    }
    
    // Exit Confirmation Dialog
    if (showExitDialog) {
        AlertDialog(
            onDismissRequest = { showExitDialog = false },
            title = { Text("退出考试") },
            text = { Text("确定要退出当前考试吗？未完成的考试将会被保存。") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showExitDialog = false
                        viewModel.pauseExam()
                        navController.popBackStack()
                    }
                ) {
                    Text("确定退出")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showExitDialog = false }
                ) {
                    Text("继续考试")
                }
            }
        )
    }
    
    // Submit Confirmation Dialog
    val showSubmitDialog by viewModel.showSubmitDialog.collectAsState()
    if (showSubmitDialog) {
        AlertDialog(
            onDismissRequest = { viewModel.hideSubmitExamDialog() },
            title = { Text("提交考试") },
            text = { 
                Column {
                    Text("确定要提交考试吗？")
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "已答题目：${examProgress.answeredQuestions} / ${examProgress.totalQuestions}",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.hideSubmitExamDialog()
                        viewModel.submitExam()
                        currentExamSession?.let { session ->
                            navController.navigate("exam_result/${session.id}") {
                                popUpTo("exam_mode") { inclusive = false }
                            }
                        }
                    }
                ) {
                    Text("确定提交")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { viewModel.hideSubmitExamDialog() }
                ) {
                    Text("继续考试")
                }
            }
        )
    }
}

@Composable
private fun ExamTopBar(
    timeRemaining: Int,
    progress: ExamViewModel.ExamProgress,
    onExitClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Timer
                TimerDisplay(timeRemaining = timeRemaining)
                
                // Exit Button
                IconButton(onClick = onExitClick) {
                    Icon(Icons.Default.Close, contentDescription = "退出考试")
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Progress Bar
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "进度",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "${progress.currentIndex + 1} / ${progress.totalQuestions}",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Spacer(modifier = Modifier.height(4.dp))
                
                LinearProgressIndicator(
                    progress = (progress.currentIndex + 1).toFloat() / progress.totalQuestions.toFloat(),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun TimerDisplay(timeRemaining: Int) {
    val minutes = timeRemaining / 60
    val seconds = timeRemaining % 60
    
    val isUrgent = timeRemaining <= 300 // Last 5 minutes
    val color = if (isUrgent) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
    
    // Blinking animation for urgent time
    val alpha by animateFloatAsState(
        targetValue = if (isUrgent && timeRemaining % 2 == 0) 0.5f else 1f,
        animationSpec = tween(durationMillis = 500),
        label = "timer_blink"
    )
    
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Default.Timer,
            contentDescription = "时间",
            tint = color.copy(alpha = alpha),
            modifier = Modifier.size(20.dp)
        )
        
        Spacer(modifier = Modifier.width(8.dp))
        
        Text(
            text = String.format("%02d:%02d", minutes, seconds),
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = color.copy(alpha = alpha)
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ExamOptionCard(
    key: String,
    value: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .selectable(
                selected = isSelected,
                onClick = onClick
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) 
                MaterialTheme.colorScheme.secondaryContainer 
            else 
                MaterialTheme.colorScheme.surface
        ),
        border = androidx.compose.foundation.BorderStroke(
            width = if (isSelected) 2.dp else 1.dp,
            color = if (isSelected) 
                MaterialTheme.colorScheme.secondary 
            else 
                MaterialTheme.colorScheme.outline
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "$key.",
                fontWeight = FontWeight.Bold,
                modifier = Modifier.width(24.dp)
            )
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Text(
                text = value,
                modifier = Modifier.weight(1f)
            )
            
            if (isSelected) {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "已选择",
                    tint = MaterialTheme.colorScheme.secondary
                )
            }
        }
    }
}
