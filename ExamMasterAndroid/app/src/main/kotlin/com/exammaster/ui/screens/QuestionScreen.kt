package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.material.icons.Icons
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
fun QuestionScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val currentQuestion by viewModel.currentQuestion.collectAsState()
    val selectedAnswers by viewModel.selectedAnswers.collectAsState()
    val showResult by viewModel.showResult.collectAsState()
    val isAnswerCorrect by viewModel.isAnswerCorrect.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    // Check if current question is favorited
    val isFavorite = remember(currentQuestion?.id) { mutableStateOf(false) }
    
    LaunchedEffect(currentQuestion?.id) {
        currentQuestion?.id?.let { questionId ->
            viewModel.isFavorite(questionId).collect { favorite ->
                isFavorite.value = favorite
            }
        }
    }
    
    // Load a question if none is loaded
    LaunchedEffect(currentQuestion) {
        if (currentQuestion == null) {
            viewModel.loadRandomQuestion()
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Top Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { navController.popBackStack() }) {
                Icon(Icons.Default.ArrowBack, contentDescription = "返回")
            }
            
            Text(
                text = "题目 ${currentQuestion?.id ?: ""}",
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium
            )
            
            IconButton(onClick = { viewModel.toggleFavorite() }) {
                Icon(
                    imageVector = if (isFavorite.value) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                    contentDescription = if (isFavorite.value) "取消收藏" else "收藏",
                    tint = if (isFavorite.value) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            currentQuestion?.let { question ->
                // Question Content
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
                            text = question.stem,
                            fontSize = 16.sp,
                            lineHeight = 24.sp,
                            modifier = Modifier.padding(bottom = 16.dp)
                        )
                        
                        // Question Type and Difficulty
                        Row {
                            AssistChip(
                                onClick = { },
                                label = { Text(question.qtype ?: "未知题型") }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            AssistChip(
                                onClick = { },
                                label = { Text("难度: ${question.difficulty ?: "未知"}") }
                            )
                        }
                    }
                }
                  // Options
                question.getFormattedOptions().forEach { (key, value) ->
                    OptionItem(
                        option = key,
                        text = value,
                        isSelected = selectedAnswers.contains(key),
                        isEnabled = !showResult,
                        onSelect = { viewModel.selectAnswer(key) },
                        isJudgmentQuestion = question.qtype == "判断题"
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Result Display
                if (showResult) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 16.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = if (isAnswerCorrect) 
                                MaterialTheme.colorScheme.primaryContainer
                            else 
                                MaterialTheme.colorScheme.errorContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = if (isAnswerCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                                    contentDescription = null,
                                    tint = if (isAnswerCorrect) 
                                        MaterialTheme.colorScheme.primary
                                    else 
                                        MaterialTheme.colorScheme.error
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = if (isAnswerCorrect) "回答正确！" else "回答错误",
                                    fontWeight = FontWeight.Bold
                                )
                            }
                              if (!isAnswerCorrect) {
                                Spacer(modifier = Modifier.height(8.dp))
                                
                                val displayAnswer = if (question.qtype == "判断题") {
                                    question.answer // 判断题直接显示 "正确"/"错误"
                                } else {
                                    question.answer // 其他题型保持原样
                                }
                                
                                Text(
                                    text = "正确答案：$displayAnswer",
                                    color = MaterialTheme.colorScheme.error
                                )
                            }
                        }
                    }
                }
                
                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    if (!showResult) {
                        Button(
                            onClick = { viewModel.submitAnswer() },
                            modifier = Modifier.weight(1f),
                            enabled = selectedAnswers.isNotEmpty()
                        ) {
                            Text("提交答案")
                        }
                    } else {
                        Button(
                            onClick = { viewModel.nextQuestion() },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("下一题")
                        }
                    }
                    
                    OutlinedButton(
                        onClick = { 
                            viewModel.loadSequentialQuestion()
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("顺序题目")
                    }
                }
            }
        }
    }
}

@Composable
private fun OptionItem(
    option: String,
    text: String,
    isSelected: Boolean,
    isEnabled: Boolean,
    onSelect: () -> Unit,
    isJudgmentQuestion: Boolean = false
) {    Card(
        modifier = Modifier
            .fillMaxWidth()
            .selectable(
                selected = isSelected,
                enabled = isEnabled,
                onClick = onSelect
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) 
                MaterialTheme.colorScheme.primaryContainer
            else 
                MaterialTheme.colorScheme.surface
        ),
        border = if (isSelected) 
            androidx.compose.foundation.BorderStroke(2.dp, MaterialTheme.colorScheme.primary)
        else if (isJudgmentQuestion) // 判断题强调单选特性
            androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
        else null
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "$option.",
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(end = 12.dp)
            )
            
            Text(
                text = text,
                modifier = Modifier.weight(1f),
                lineHeight = 20.sp
            )
            
            if (isSelected) {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "已选择",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}