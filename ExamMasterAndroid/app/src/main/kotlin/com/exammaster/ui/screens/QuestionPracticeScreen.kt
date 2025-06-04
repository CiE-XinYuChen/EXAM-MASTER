package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuestionPracticeScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val currentQuestion by viewModel.currentQuestion.collectAsState()
    val selectedAnswers by viewModel.selectedAnswers.collectAsState()
    val showResult by viewModel.showResult.collectAsState()
    val isAnswerCorrect by viewModel.isAnswerCorrect.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val currentMode by viewModel.currentMode.collectAsState()
    
    // Check if current question is favorited
    var isFavorited by remember { mutableStateOf(false) }
    
    LaunchedEffect(currentQuestion?.id) {
        currentQuestion?.id?.let { questionId ->
            viewModel.isFavorite(questionId).collect { isFav ->
                isFavorited = isFav
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
    
    currentQuestion?.let { question ->
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
                    text = when (currentMode) {
                        ExamViewModel.QuizMode.RANDOM -> "随机练习"
                        ExamViewModel.QuizMode.SEQUENTIAL -> "顺序练习"
                        ExamViewModel.QuizMode.WRONG_ONLY -> "错题练习"
                        else -> "练习模式"
                    },
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Medium
                )
                
                IconButton(onClick = { viewModel.toggleFavorite() }) {
                    Icon(
                        if (isFavorited) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                        contentDescription = if (isFavorited) "取消收藏" else "收藏",
                        tint = if (isFavorited) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Question Info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "题目 ${question.id}",
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
                        OptionCard(
                            key = key,
                            value = value,
                            isSelected = selectedAnswers.contains(key),
                            isCorrect = if (showResult) question.answer.contains(key) else null,
                            isUserSelected = if (showResult) selectedAnswers.contains(key) else false,
                            enabled = !showResult,
                            onClick = { 
                                if (!showResult) {
                                    viewModel.selectAnswer(key)
                                }
                            }
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // Result Display
            if (showResult) {
                ResultCard(
                    isCorrect = isAnswerCorrect,
                    correctAnswer = question.answer,
                    userAnswer = selectedAnswers.sorted().joinToString("")
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Next Question Button
                Button(
                    onClick = { viewModel.nextQuestion() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("下一题")
                }
            } else {
                // Submit Button
                Button(
                    onClick = { viewModel.submitAnswer() },
                    enabled = selectedAnswers.isNotEmpty(),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("提交答案")
                }
            }
        }
    } ?: run {
        // No question available
        EmptyQuestionState(
            mode = currentMode,
            onBackClick = { navController.popBackStack() },
            onRetryClick = { viewModel.loadNextQuestion() }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun OptionCard(
    key: String,
    value: String,
    isSelected: Boolean,
    isCorrect: Boolean?,
    isUserSelected: Boolean,
    enabled: Boolean,
    onClick: () -> Unit
) {
    val backgroundColor = when {
        isCorrect == true -> MaterialTheme.colorScheme.primaryContainer
        isCorrect == false && isUserSelected -> MaterialTheme.colorScheme.errorContainer
        isSelected -> MaterialTheme.colorScheme.secondaryContainer
        else -> MaterialTheme.colorScheme.surface
    }
    
    val borderColor = when {
        isCorrect == true -> MaterialTheme.colorScheme.primary
        isCorrect == false && isUserSelected -> MaterialTheme.colorScheme.error
        isSelected -> MaterialTheme.colorScheme.secondary
        else -> MaterialTheme.colorScheme.outline
    }
    
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .selectable(
                selected = isSelected,
                onClick = onClick,
                enabled = enabled
            ),
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        border = androidx.compose.foundation.BorderStroke(
            width = if (isSelected || isCorrect != null) 2.dp else 1.dp,
            color = borderColor
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
            
            if (isCorrect == true) {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "正确",
                    tint = MaterialTheme.colorScheme.primary
                )
            } else if (isCorrect == false && isUserSelected) {
                Icon(
                    imageVector = Icons.Default.Cancel,
                    contentDescription = "错误",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun ResultCard(
    isCorrect: Boolean,
    correctAnswer: String,
    userAnswer: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isCorrect) 
                MaterialTheme.colorScheme.primaryContainer 
            else 
                MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                    contentDescription = if (isCorrect) "正确" else "错误",
                    tint = if (isCorrect) 
                        MaterialTheme.colorScheme.primary 
                    else 
                        MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(32.dp)
                )
                
                Spacer(modifier = Modifier.width(16.dp))
                
                Text(
                    text = if (isCorrect) "回答正确！" else "回答错误",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (isCorrect) 
                        MaterialTheme.colorScheme.primary 
                    else 
                        MaterialTheme.colorScheme.error
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "正确答案",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = correctAnswer,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                Column {
                    Text(
                        text = "您的答案",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = userAnswer.ifEmpty { "未选择" },
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
private fun DifficultyChip(difficulty: String) {
    val color = when (difficulty.lowercase()) {
        "easy", "简单" -> MaterialTheme.colorScheme.primary
        "medium", "中等" -> MaterialTheme.colorScheme.tertiary
        "hard", "困难" -> MaterialTheme.colorScheme.error
        else -> MaterialTheme.colorScheme.secondary
    }
    
    AssistChip(
        onClick = { },
        label = { 
            Text(
                text = difficulty,
                fontSize = 12.sp
            ) 
        },
        colors = AssistChipDefaults.assistChipColors(
            labelColor = color
        )
    )
}

@Composable
private fun CategoryChip(category: String) {
    AssistChip(
        onClick = { },
        label = { 
            Text(
                text = category,
                fontSize = 12.sp
            ) 
        }
    )
}

@Composable
private fun EmptyQuestionState(
    mode: ExamViewModel.QuizMode,
    onBackClick: () -> Unit,
    onRetryClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.HelpOutline,
            contentDescription = "无题目",
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = when (mode) {
                ExamViewModel.QuizMode.WRONG_ONLY -> "暂无错题"
                else -> "暂无可用题目"
            },
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = when (mode) {
                ExamViewModel.QuizMode.WRONG_ONLY -> "您还没有答错的题目，继续保持！"
                else -> "请检查题库数据是否正确导入"
            },
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedButton(onClick = onBackClick) {
                Text("返回")
            }
            
            Button(onClick = onRetryClick) {
                Text("重试")
            }
        }
    }
}
