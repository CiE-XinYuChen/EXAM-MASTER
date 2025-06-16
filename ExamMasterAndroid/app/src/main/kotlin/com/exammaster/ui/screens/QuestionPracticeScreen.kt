// QuestionPracticeScreen.kt
package com.exammaster.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
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

/* -------------------------------------------------------------------------- */
/*  练习主页面                                                                 */
/* -------------------------------------------------------------------------- */
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
    val statistics by viewModel.statistics.collectAsState()

    /* ---------- 收藏状态 ---------- */
    var isFavorited by remember { mutableStateOf(false) }
    var attemptCount by remember { mutableStateOf(0) }
    
    LaunchedEffect(currentQuestion?.id) {
        currentQuestion?.id?.let { id ->
            viewModel.isFavorite(id).collect { fav -> isFavorited = fav }
        }
    }
    
    LaunchedEffect(currentQuestion?.id) {
        currentQuestion?.id?.let { id ->
            viewModel.getQuestionAttemptCount(id).collect { count -> attemptCount = count }
        }
    }

    /* ---------- 加载中 ---------- */
    if (isLoading) {
        Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
        return
    }

    /* ---------- 动画切换题目 ---------- */
    AnimatedQuestionContent(
        targetState = currentQuestion?.id ?: "empty",
        modifier = Modifier.fillMaxSize()
    ) { state ->
        if (state == "empty") {
            /* 无题目 */
            EmptyQuestionState(
                mode = currentMode,
                onBackClick = { navController.popBackStack() },
                onRetryClick = { viewModel.loadRandomQuestion() }
            )
            return@AnimatedQuestionContent
        }

        /* 有题目 */
        currentQuestion?.let { question ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp)
            ) {

                /* ---------------- 顶部栏 ---------------- */
                Column {
                    Row(
                        Modifier.fillMaxWidth(),
                        Arrangement.SpaceBetween,
                        Alignment.CenterVertically
                    ) {
                        IconButton({ navController.popBackStack() }) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                        }
                        Text(
                            text = when (currentMode) {
                                ExamViewModel.QuizMode.RANDOM      -> "随机练习"
                                ExamViewModel.QuizMode.SEQUENTIAL  -> "顺序练习"
                                ExamViewModel.QuizMode.WRONG_ONLY  -> "错题练习"
                                else                               -> "练习模式"
                            },
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Medium
                        )
                        IconButton({ viewModel.toggleFavorite() }) {
                            Icon(
                                if (isFavorited) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                                contentDescription = if (isFavorited) "取消收藏" else "收藏",
                                tint = if (isFavorited)
                                    MaterialTheme.colorScheme.error
                                else
                                    MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                    
                    /* ---------------- 进度条 ---------------- */
                    if (statistics.totalQuestions > 0) {
                        val progress = statistics.answeredQuestions.toFloat() / statistics.totalQuestions.toFloat()
                        val percentage = (progress * 100).toInt()
                        Column(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 2.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "${statistics.answeredQuestions}/${statistics.totalQuestions}",
                                    fontSize = 11.sp,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Text(
                                    text = "$percentage%",
                                    fontSize = 11.sp,
                                    color = MaterialTheme.colorScheme.primary,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                            LinearProgressIndicator(
                                progress = { progress },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(2.dp)
                                    .padding(horizontal = 16.dp),
                                color = MaterialTheme.colorScheme.primary,
                                trackColor = MaterialTheme.colorScheme.surfaceVariant,
                            )
                        }
                    }
                }

                Spacer(Modifier.height(12.dp))

                /* ---------------- 题干 ---------------- */
                Box(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 10.dp) // 为镶嵌标签留出空间，减小一点
                    ) {
                        Column(
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 20.dp)
                                .padding(top = 20.dp, bottom = 12.dp) // 稍微增加顶部间距，避免标签太近
                        ) {
                            Text(text = question.stem, fontSize = 16.sp, lineHeight = 24.sp)
                        }
                    }
                    
                    /* ---------------- 镶嵌在卡片边缘的标签 ---------------- */
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Surface(
                                color = MaterialTheme.colorScheme.primary,
                                shape = RoundedCornerShape(5.dp),
                                shadowElevation = 3.dp
                            ) {
                                Text(
                                    text = "题目 ${question.id}",
                                    color = androidx.compose.ui.graphics.Color.White,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                )
                            }
                            
                            // 作答次数标签
                            if (attemptCount > 0) {
                                Spacer(modifier = Modifier.width(6.dp))
                                Surface(
                                    color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.9f),
                                    shape = RoundedCornerShape(10.dp),
                                    shadowElevation = 2.dp
                                ) {
                                    Text(
                                        text = "第${attemptCount}次",
                                        fontSize = 9.sp,
                                        color = MaterialTheme.colorScheme.primary,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp),
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                            }
                        }
                        
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // 题型标签
                            question.qtype?.let { qtype ->
                                Surface(
                                    shadowElevation = 2.dp,
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    CompactQuestionTypeChip(qtype = qtype)
                                }
                            }
                            // 难度标签 - 过滤掉"无"
                            question.difficulty?.takeIf { it != "无" && it.isNotBlank() }?.let { difficulty ->
                                Surface(
                                    shadowElevation = 2.dp,
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    CompactDifficultyChip(difficulty = difficulty)
                                }
                            }
                            // 分类标签 - 过滤掉"未分类"
                            question.category?.takeIf { it != "未分类" && it.isNotBlank() }?.let { category ->
                                Surface(
                                    shadowElevation = 2.dp,
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    CompactCategoryChip(category = category)
                                }
                            }
                        }
                    }
                }

                Spacer(Modifier.height(20.dp))

                /* ---------------- 选项 ---------------- */
                if (question.getFormattedOptions().isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        question.getFormattedOptions().forEach { (key, value) ->
                            val isCorrectOption =
                                if (showResult) {
                                    if (question.qtype == "判断题") {
                                        when (key) {
                                            "A"  -> question.answer == "正确"
                                            "B"  -> question.answer == "错误"
                                            else -> false
                                        }
                                    } else {
                                        question.answer.contains(key)
                                    }
                                } else null

                            OptionCard(
                                key = key,
                                value = value,
                                isSelected = selectedAnswers.contains(key),
                                isCorrect = isCorrectOption,
                                isUserSelected = showResult && selectedAnswers.contains(key),
                                enabled = !showResult,
                                onClick = {
                                    if (!showResult) viewModel.selectAnswer(key)
                                }
                            )
                        }
                    }
                }

                Spacer(Modifier.height(24.dp))

                /* ---------------- 结果 / 下一题 / 提交 ---------------- */
                if (showResult) {
                    ResultCard(
                        isCorrect = isAnswerCorrect,
                        correctAnswer = question.answer,
                        userAnswer = selectedAnswers.sorted().joinToString(""),
                        isJudgmentQuestion = question.qtype == "判断题"
                    )
                    Spacer(Modifier.height(12.dp))
                    Button(
                        onClick = { viewModel.nextQuestion() },
                        modifier = Modifier.fillMaxWidth()
                    ) { Text("下一题") }
                } else {
                    Button(
                        onClick = { viewModel.submitAnswer() },
                        enabled = selectedAnswers.isNotEmpty(),
                        modifier = Modifier.fillMaxWidth()
                    ) { Text("提交答案") }
                }
            }
        }
    }
}

/* -------------------------------------------------------------------------- */
/*  OptionCard – 单个选项                                                     */
/* -------------------------------------------------------------------------- */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OptionCard(
    key: String,
    value: String,
    isSelected: Boolean,
    isCorrect: Boolean?,
    isUserSelected: Boolean,
    enabled: Boolean,
    onClick: () -> Unit
) {
    val bgColor = when {
        isCorrect == true                       -> MaterialTheme.colorScheme.primaryContainer
        isCorrect == false && isUserSelected    -> MaterialTheme.colorScheme.errorContainer
        isSelected                              -> MaterialTheme.colorScheme.secondaryContainer
        else                                    -> MaterialTheme.colorScheme.surface
    }
    val strokeColor = when {
        isCorrect == true                       -> MaterialTheme.colorScheme.primary
        isCorrect == false && isUserSelected    -> MaterialTheme.colorScheme.error
        isSelected                              -> MaterialTheme.colorScheme.secondary
        else                                    -> MaterialTheme.colorScheme.outline
    }

    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .selectable(selected = isSelected, enabled = enabled, onClick = onClick), // Corrected line
        colors = CardDefaults.cardColors(containerColor = bgColor),
        border = BorderStroke(
            width = if (isSelected || isCorrect != null) 2.dp else 1.dp,
            color = strokeColor
        )
    ) {
        Row(
            Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "$key.",
                fontWeight = FontWeight.Bold,
                modifier = Modifier.width(24.dp)
            )
            Spacer(Modifier.width(12.dp))
            Text(value, modifier = Modifier.weight(1f))
            when {
                isCorrect == true -> Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "正确",
                    tint = MaterialTheme.colorScheme.primary
                )
                isCorrect == false && isUserSelected -> Icon(
                    imageVector = Icons.Default.Cancel,
                    contentDescription = "错误",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

/* -------------------------------------------------------------------------- */
/*  ResultCard – 精简版答案结果                                               */
/* -------------------------------------------------------------------------- */
@Composable
fun ResultCard(
    isCorrect: Boolean,
    correctAnswer: String,
    userAnswer: String,
    isJudgmentQuestion: Boolean = false
) {
    val displayUserAnswer = if (isJudgmentQuestion) {
        when (userAnswer) {
            "A"  -> "正确"
            "B"  -> "错误"
            else -> if (userAnswer.isBlank()) "未选择" else userAnswer
        }
    } else {
        if (userAnswer.isBlank()) "未选择" else userAnswer
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = if (isCorrect)
            MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.7f)
        else
            MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.7f),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            // 左侧：结果图标和状态
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                    contentDescription = if (isCorrect) "正确" else "错误",
                    tint = if (isCorrect) MaterialTheme.colorScheme.primary
                           else MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = if (isCorrect) "正确" else "错误",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = if (isCorrect) MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.error
                )
            }
            
            // 右侧：答案对比
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // 正确答案
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    Text(
                        text = "正确答案",
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = correctAnswer,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                // 分隔符
                Text(
                    text = "vs",
                    fontSize = 10.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // 用户答案
                Column(
                    horizontalAlignment = Alignment.Start
                ) {
                    Text(
                        text = "您的答案",
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = displayUserAnswer,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (isCorrect) MaterialTheme.colorScheme.primary
                                else MaterialTheme.colorScheme.error
                    )
                }
            }
        }
    }
}

/* -------------------------------------------------------------------------- */
/*  DifficultyChip                                                            */
/* -------------------------------------------------------------------------- */
@Composable
fun DifficultyChip(difficulty: String) {
    val chipColor = when (difficulty.lowercase()) {
        "easy", "简单"   -> MaterialTheme.colorScheme.primary
        "medium", "中等" -> MaterialTheme.colorScheme.tertiary
        "hard", "困难"  -> MaterialTheme.colorScheme.error
        else             -> MaterialTheme.colorScheme.secondary
    }

    AssistChip(
        onClick = { },
        label = { Text(difficulty, fontSize = 12.sp) },
        colors = AssistChipDefaults.assistChipColors(labelColor = chipColor)
    )
}

/* -------------------------------------------------------------------------- */
/*  CategoryChip                                                              */
/* -------------------------------------------------------------------------- */
@Composable
fun CategoryChip(category: String) {
    AssistChip(
        onClick = { },
        label = { Text(category, fontSize = 12.sp) }
    )
}

/* -------------------------------------------------------------------------- */
/*  QuestionTypeChip                                                          */
/* -------------------------------------------------------------------------- */
@Composable
fun QuestionTypeChip(qtype: String) {
    val (chipColor, iconVector) = when (qtype) {
        "单选题" -> MaterialTheme.colorScheme.primary to Icons.Default.RadioButtonChecked
        "多选题" -> MaterialTheme.colorScheme.secondary to Icons.Default.CheckBox
        "判断题" -> MaterialTheme.colorScheme.tertiary to Icons.Default.ToggleOn
        "填空题" -> MaterialTheme.colorScheme.outline to Icons.Default.Edit
        else -> MaterialTheme.colorScheme.onSurfaceVariant to Icons.Default.Quiz
    }

    AssistChip(
        onClick = { },
        label = { Text(qtype, fontSize = 12.sp) },
        leadingIcon = {
            Icon(
                imageVector = iconVector,
                contentDescription = qtype,
                modifier = Modifier.size(16.dp)
            )
        },
        colors = AssistChipDefaults.assistChipColors(
            labelColor = chipColor,
            leadingIconContentColor = chipColor
        )
    )
}

/* -------------------------------------------------------------------------- */
/*  Compact Chip Components                                                   */
/* -------------------------------------------------------------------------- */
@Composable
fun CompactQuestionTypeChip(qtype: String) {
    val (chipColor, iconVector) = when (qtype) {
        "单选题" -> MaterialTheme.colorScheme.primary to Icons.Default.RadioButtonChecked
        "多选题" -> MaterialTheme.colorScheme.secondary to Icons.Default.CheckBox
        "判断题" -> MaterialTheme.colorScheme.tertiary to Icons.Default.ToggleOn
        "填空题" -> MaterialTheme.colorScheme.outline to Icons.Default.Edit
        else -> MaterialTheme.colorScheme.onSurfaceVariant to Icons.Default.Quiz
    }

    AssistChip(
        onClick = { },
        label = { Text(qtype, fontSize = 10.sp) },
        leadingIcon = {
            Icon(
                imageVector = iconVector,
                contentDescription = qtype,
                modifier = Modifier.size(12.dp)
            )
        },
        colors = AssistChipDefaults.assistChipColors(
            labelColor = chipColor,
            leadingIconContentColor = chipColor
        ),
        modifier = Modifier.height(20.dp)
    )
}

@Composable
fun CompactDifficultyChip(difficulty: String) {
    val chipColor = when (difficulty.lowercase()) {
        "easy", "简单"   -> MaterialTheme.colorScheme.primary
        "medium", "中等" -> MaterialTheme.colorScheme.tertiary
        "hard", "困难"  -> MaterialTheme.colorScheme.error
        else             -> MaterialTheme.colorScheme.secondary
    }

    AssistChip(
        onClick = { },
        label = { Text(difficulty, fontSize = 10.sp) },
        colors = AssistChipDefaults.assistChipColors(labelColor = chipColor),
        modifier = Modifier.height(20.dp)
    )
}

@Composable
fun CompactCategoryChip(category: String) {
    AssistChip(
        onClick = { },
        label = { Text(category, fontSize = 10.sp) },
        modifier = Modifier.height(20.dp)
    )
}

/* -------------------------------------------------------------------------- */
/*  EmptyQuestionState                                                        */
/* -------------------------------------------------------------------------- */
@Composable
fun EmptyQuestionState(
    mode: ExamViewModel.QuizMode,
    onBackClick: () -> Unit,
    onRetryClick: () -> Unit
) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            Icons.Default.HelpOutline,
            contentDescription = "无题目",
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(16.dp))
        Text(
            text = if (mode == ExamViewModel.QuizMode.WRONG_ONLY) "暂无错题" else "暂无可用题目",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = if (mode == ExamViewModel.QuizMode.WRONG_ONLY)
                "您还没有答错的题目，继续保持！"
            else
                "请检查题库数据是否正确导入",
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(32.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            OutlinedButton(onClick = onBackClick) { Text("返回") }
            Button(onClick = onRetryClick)         { Text("重试") }
        }
    }
}
