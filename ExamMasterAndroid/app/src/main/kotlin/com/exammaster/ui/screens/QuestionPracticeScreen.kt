// QuestionPracticeScreen.kt
package com.exammaster.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.foundation.BorderStroke
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

/* -------------------------------------------------------------------------- */
/*  Animated wrapper – 封装题目切换动效                                         */
/* -------------------------------------------------------------------------- */
// @OptIn(ExperimentalAnimationApi::class)
// @Composable
// fun <T> AnimatedQuestionContent(
// targetState: T,
// modifier: Modifier = Modifier,
//    content: @Composable (T) -> Unit
// ) {
// AnimatedContent(
// targetState = targetState,
// modifier = modifier,
// label = "questionAnimatedContent",
// content = content
// )
// }

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

    /* ---------- 收藏状态 ---------- */
    var isFavorited by remember { mutableStateOf(false) }
    LaunchedEffect(currentQuestion?.id) {
        currentQuestion?.id?.let { id ->
            viewModel.isFavorite(id).collect { fav -> isFavorited = fav }
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

                Spacer(Modifier.height(16.dp))

                /* ---------------- 题目信息 ---------------- */
                Row(
                    Modifier.fillMaxWidth(),
                    Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "题目 ${question.id}",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Row {
                        question.difficulty?.let {
                            DifficultyChip(difficulty = it)
                            Spacer(Modifier.width(8.dp))
                        }
                        question.category?.let { CategoryChip(category = it) }
                    }
                }

                Spacer(Modifier.height(24.dp))

                /* ---------------- 题干 ---------------- */
                Card(Modifier.fillMaxWidth()) {
                    Column(
                        Modifier
                            .fillMaxWidth()
                            .padding(20.dp)
                    ) {
                        Text(
                            text = "题目",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(Modifier.height(12.dp))
                        Text(text = question.stem, fontSize = 16.sp, lineHeight = 24.sp)
                    }
                }

                Spacer(Modifier.height(24.dp))

                /* ---------------- 选项 ---------------- */
                if (question.getFormattedOptions().isNotEmpty()) {
                    Text(
                        text = "选择答案",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(Modifier.height(12.dp))

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

                Spacer(Modifier.height(32.dp))

                /* ---------------- 结果 / 下一题 / 提交 ---------------- */
                if (showResult) {
                    ResultCard(
                        isCorrect = isAnswerCorrect,
                        correctAnswer = question.answer,
                        userAnswer = selectedAnswers.sorted().joinToString(""),
                        isJudgmentQuestion = question.qtype == "判断题"
                    )
                    Spacer(Modifier.height(24.dp))
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
/*  ResultCard – 答案结果                                                     */
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

    Card(
        Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isCorrect)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                    contentDescription = if (isCorrect) "正确" else "错误",
                    tint = if (isCorrect) MaterialTheme.colorScheme.primary
                           else MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(Modifier.width(16.dp))
                Text(
                    text = if (isCorrect) "回答正确！" else "回答错误",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (isCorrect) MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.error
                )
            }

            Spacer(Modifier.height(16.dp))

            Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
                Column {
                    Text("正确答案", fontSize = 14.sp,
                         color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(correctAnswer, fontSize = 16.sp, fontWeight = FontWeight.Medium)
                }
                Column {
                    Text("您的答案", fontSize = 14.sp,
                         color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(displayUserAnswer, fontSize = 16.sp, fontWeight = FontWeight.Medium)
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
