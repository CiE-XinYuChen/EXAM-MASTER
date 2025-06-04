package com.exammaster.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel
import com.patrykandpatrick.vico.compose.axis.horizontal.bottomAxis
import com.patrykandpatrick.vico.compose.axis.vertical.startAxis
import com.patrykandpatrick.vico.compose.chart.Chart
import com.patrykandpatrick.vico.compose.chart.column.columnChart
import com.patrykandpatrick.vico.compose.chart.line.lineChart
import com.patrykandpatrick.vico.compose.component.shape.shader.fromBrush
import com.patrykandpatrick.vico.core.DefaultColors
import com.patrykandpatrick.vico.core.chart.column.ColumnChart
import com.patrykandpatrick.vico.core.chart.line.LineChart
import com.patrykandpatrick.vico.core.component.shape.shader.DynamicShaders
import com.patrykandpatrick.vico.core.entry.ChartEntryModelProducer
import com.patrykandpatrick.vico.core.entry.FloatEntry
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatisticsScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val statistics by viewModel.statistics.collectAsState()
    val advancedStatistics by viewModel.advancedStatistics.collectAsState()
    var selectedTab by remember { mutableStateOf(0) }
    
    // Load advanced statistics when screen is composed
    LaunchedEffect(Unit) {
        viewModel.loadAdvancedStatistics()
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Top Bar
        TopAppBar(
            title = {
                Text(
                    text = "统计分析 🔄",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
            },
            navigationIcon = {
                IconButton(onClick = { navController.popBackStack() }) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                }
            },
            actions = {
                IconButton(onClick = { viewModel.loadAdvancedStatistics() }) {
                    Icon(Icons.Default.Refresh, contentDescription = "刷新")
                }
            }
        )
        
        // Tab Row
        TabRow(
            selectedTabIndex = selectedTab,
            modifier = Modifier.fillMaxWidth()
        ) {
            Tab(
                selected = selectedTab == 0,
                onClick = { selectedTab = 0 },
                text = { Text("概览") }
            )
            Tab(
                selected = selectedTab == 1,
                onClick = { selectedTab = 1 },
                text = { Text("图表") }
            )
            Tab(
                selected = selectedTab == 2,
                onClick = { selectedTab = 2 },
                text = { Text("历史") }
            )
            Tab(
                selected = selectedTab == 3,
                onClick = { selectedTab = 3 },
                text = { Text("分析") }
            )
        }
        
        // Content based on selected tab
        when (selectedTab) {
            0 -> OverviewTab(statistics, advancedStatistics, viewModel)
            1 -> ChartsTab(advancedStatistics)
            2 -> HistoryTab(advancedStatistics)
            3 -> AnalysisTab(statistics, advancedStatistics, navController, viewModel)
        }
    }
}

// Overview Tab - 概览标签页
@Composable
private fun OverviewTab(
    statistics: ExamViewModel.Statistics,
    advancedStatistics: ExamViewModel.AdvancedStatistics?,
    viewModel: ExamViewModel
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Key Metrics Row
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "关键指标",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        item {
                            MetricCard(
                                icon = Icons.Default.Quiz,
                                label = "总题数",
                                value = statistics.totalQuestions.toString(),
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                        item {
                            MetricCard(
                                icon = Icons.Default.Assignment,
                                label = "已答题",
                                value = statistics.answeredQuestions.toString(),
                                color = MaterialTheme.colorScheme.secondary
                            )
                        }
                        item {
                            MetricCard(
                                icon = Icons.Default.TrendingUp,
                                label = "答题次数",
                                value = statistics.totalAnswers.toString(),
                                color = MaterialTheme.colorScheme.tertiary
                            )
                        }
                        item {
                            MetricCard(
                                icon = Icons.Default.Percent,
                                label = "正确率",
                                value = "%.1f%%".format(statistics.accuracy),
                                color = if (statistics.accuracy >= 80) Color(0xFF4CAF50) else Color(0xFFFF9800)
                            )
                        }
                    }
                }
            }
        }
        
        // Weekly Progress
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "本周学习情况",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceAround
                    ) {                        WeeklyProgressItem(
                            label = "本周答题",
                            value = advancedStatistics?.weeklyCount ?: 0,
                            icon = Icons.Default.CalendarToday
                        )
                        WeeklyProgressItem(
                            label = "本月答题",
                            value = advancedStatistics?.monthlyCount ?: 0,
                            icon = Icons.Default.CalendarMonth
                        )
                    }
                }
            }
        }
        
        // Learning Progress
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "学习进度",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    val progress = if (statistics.totalQuestions > 0) {
                        statistics.answeredQuestions.toFloat() / statistics.totalQuestions.toFloat()
                    } else 0f
                    
                    LinearProgressIndicator(
                        progress = progress,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(12.dp)
                            .clip(RoundedCornerShape(6.dp)),
                        color = MaterialTheme.colorScheme.primary,
                        trackColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "${statistics.answeredQuestions} / ${statistics.totalQuestions} 题",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "%.1f%%".format(progress * 100),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
        }
          // Category Distribution
        item {
            advancedStatistics?.categoryStats?.let { categoryStats ->
                if (categoryStats.isNotEmpty()) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Text(
                                text = "分类答题情况",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(bottom = 16.dp)                            )
                            
                            for (category in categoryStats.take(5)) {
                                CategoryProgressItem(
                                    category = category.category,
                                    correct = category.correctCount,
                                    total = category.totalCount,
                                    accuracy = category.accuracy
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                            }
                        }
                    }
                }
            }
        }
    }
}

// Charts Tab - 图表标签页
@Composable
private fun ChartsTab(advancedStatistics: ExamViewModel.AdvancedStatistics?) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Daily Activity Chart
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "每日答题统计",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    advancedStatistics?.dailyStats?.let { dailyStats ->
                        if (dailyStats.isNotEmpty()) {
                            DailyActivityChart(dailyStats)
                        } else {
                            EmptyChartPlaceholder("暂无每日数据")
                        }
                    } ?: EmptyChartPlaceholder("加载中...")
                }
            }
        }
        
        // Category Performance Chart
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "分类表现对比",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    advancedStatistics?.categoryStats?.let { categoryStats ->
                        if (categoryStats.isNotEmpty()) {
                            CategoryPerformanceChart(categoryStats)
                        } else {
                            EmptyChartPlaceholder("暂无分类数据")
                        }
                    } ?: EmptyChartPlaceholder("加载中...")
                }
            }
        }
        
        // Difficulty Analysis Chart
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "难度分析",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    advancedStatistics?.difficultyStats?.let { difficultyStats ->
                        if (difficultyStats.isNotEmpty()) {
                            DifficultyAnalysisChart(difficultyStats)
                        } else {
                            EmptyChartPlaceholder("暂无难度数据")
                        }
                    } ?: EmptyChartPlaceholder("加载中...")
                }
            }
        }
    }
}

// History Tab - 历史标签页
@Composable
private fun HistoryTab(advancedStatistics: ExamViewModel.AdvancedStatistics?) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "答题历史记录",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 8.dp)
            )
        }
        
        advancedStatistics?.recentHistory?.let { history ->
            if (history.isNotEmpty()) {
                items(history) { historyItem ->
                    HistoryItem(historyItem)
                }
            } else {
                item {
                    EmptyHistoryPlaceholder()
                }
            }
        } ?: item {
            LoadingPlaceholder()
        }
    }
}

// Analysis Tab - 分析标签页
@Composable
private fun AnalysisTab(
    statistics: ExamViewModel.Statistics,
    advancedStatistics: ExamViewModel.AdvancedStatistics?,
    navController: NavController,
    viewModel: ExamViewModel
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Performance Analysis
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "表现分析",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    PerformanceAnalysis(statistics)
                }
            }
        }
        
        // Most Attempted Questions
        item {
            advancedStatistics?.mostAttempted?.let { questions ->
                if (questions.isNotEmpty()) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Text(
                                text = "常答题目",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(bottom = 16.dp)                            )
                            
                            for (question in questions.take(5)) {
                                MostAttemptedQuestionItem(question)
                                Spacer(modifier = Modifier.height(8.dp))
                            }
                        }
                    }
                }
            }
        }
        
        // Quick Actions
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "快速操作",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Button(
                            onClick = { 
                                viewModel.loadSequentialQuestion()
                                navController.navigate("question")
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.PlayArrow,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("开始答题")
                        }
                        
                        OutlinedButton(
                            onClick = { 
                                viewModel.resetHistory()
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("重置记录")
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedButton(
                        onClick = { 
                            viewModel.clearAllUserData()
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Default.DeleteForever,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("清除所有数据")
                    }
                }
            }
        }
    }
}

// Supporting Components - 支持组件

@Composable
private fun MetricCard(
    icon: ImageVector,
    label: String,
    value: String,
    color: Color
) {
    Card(
        modifier = Modifier
            .width(120.dp)
            .height(100.dp),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = color,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = color,
                textAlign = TextAlign.Center
            )
            Text(
                text = label,
                fontSize = 10.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun WeeklyProgressItem(
    label: String,
    value: Int,
    icon: ImageVector
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(32.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = value.toString(),
            fontSize = 24.sp,
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

@Composable
private fun CategoryProgressItem(
    category: String,
    correct: Int,
    total: Int,
    accuracy: Double
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = category,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = "%.1f%% ($correct/$total)".format(accuracy),
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        LinearProgressIndicator(
            progress = if (total > 0) correct.toFloat() / total.toFloat() else 0f,
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp)),
            color = when {
                accuracy >= 80 -> Color(0xFF4CAF50)
                accuracy >= 60 -> Color(0xFFFF9800)
                else -> Color(0xFFf44336)
            },
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
    }
}

@Composable
private fun HistoryItem(historyItem: com.exammaster.data.database.dao.HistoryWithQuestion) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = historyItem.questionContent,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        maxLines = 2
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "分类: ${historyItem.category}",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (historyItem.isCorrect) 
                                Color(0xFF4CAF50).copy(alpha = 0.1f)
                            else 
                                Color(0xFFf44336).copy(alpha = 0.1f)
                        )
                    ) {
                        Text(
                            text = if (historyItem.isCorrect) "正确" else "错误",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (historyItem.isCorrect) Color(0xFF4CAF50) else Color(0xFFf44336),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(4.dp))
                      Text(
                        text = SimpleDateFormat("MM-dd HH:mm", Locale.getDefault())
                            .format(Date(historyItem.timestamp.toLongOrNull() ?: 0L)),
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun MostAttemptedQuestionItem(question: com.exammaster.data.database.dao.QuestionAttemptStatistic) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = question.questionContent,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1
                )
                Text(
                    text = "答题 ${question.attemptCount} 次",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = "${question.attemptCount}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }
    }
}

@Composable
private fun PerformanceAnalysis(statistics: ExamViewModel.Statistics) {
    Column {
        // Accuracy Level Analysis
        val accuracyLevel = when {
            statistics.accuracy >= 90 -> "优秀" to Color(0xFF4CAF50)
            statistics.accuracy >= 80 -> "良好" to Color(0xFF8BC34A)
            statistics.accuracy >= 70 -> "中等" to Color(0xFFFF9800)
            statistics.accuracy >= 60 -> "及格" to Color(0xFFFF5722)
            else -> "需要提高" to Color(0xFFf44336)
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "表现等级",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = accuracyLevel.second.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = accuracyLevel.first,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = accuracyLevel.second,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Progress Analysis
        val progress = if (statistics.totalQuestions > 0) {
            statistics.answeredQuestions.toFloat() / statistics.totalQuestions.toFloat()
        } else 0f
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "学习进度",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            
            Text(
                text = when {
                    progress >= 0.9f -> "即将完成"
                    progress >= 0.7f -> "进展良好"
                    progress >= 0.5f -> "稳步推进"
                    progress >= 0.3f -> "刚刚起步"
                    else -> "开始学习"
                },
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Medium
            )
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Recommendations
        Text(
            text = "建议",
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium
        )
        
        Spacer(modifier = Modifier.height(4.dp))
        
        val recommendation = when {
            statistics.accuracy < 60 -> "建议回顾基础知识，加强练习"
            statistics.accuracy < 80 -> "继续努力，注意错题复习"
            progress < 0.5f -> "保持当前学习节奏，继续完成更多题目"
            else -> "表现优秀，可以尝试更有挑战性的题目"
        }
        
        Text(
            text = recommendation,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            lineHeight = 16.sp
        )
    }
}

// Chart Components - 图表组件

@Composable
private fun DailyActivityChart(dailyStats: List<com.exammaster.data.database.dao.DailyStatistic>) {
    if (dailyStats.isEmpty()) {
        EmptyChartPlaceholder("暂无数据")
        return
    }
    
    val chartEntryProducer = remember { ChartEntryModelProducer() }
    
    LaunchedEffect(dailyStats) {
        val entries = dailyStats.mapIndexed { index, stat ->
            FloatEntry(index.toFloat(), stat.totalAnswers.toFloat())
        }
        chartEntryProducer.setEntries(entries)
    }
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
    ) {
        Chart(
            chart = lineChart(),
            chartModelProducer = chartEntryProducer,
            startAxis = startAxis(),
            bottomAxis = bottomAxis()
        )
    }
}

@Composable
private fun CategoryPerformanceChart(categoryStats: List<com.exammaster.data.database.dao.CategoryStatistic>) {
    if (categoryStats.isEmpty()) {
        EmptyChartPlaceholder("暂无数据")
        return    }
    
    val chartEntryProducer = remember { ChartEntryModelProducer() }
    
    LaunchedEffect(categoryStats) {
        val entries = categoryStats.mapIndexed { index, stat ->
            FloatEntry(index.toFloat(), stat.accuracy.toFloat())
        }
        chartEntryProducer.setEntries(entries)
    }
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
    ) {
        Chart(
            chart = columnChart(),
            chartModelProducer = chartEntryProducer,
            startAxis = startAxis(),
            bottomAxis = bottomAxis()
        )
    }
}

@Composable
private fun DifficultyAnalysisChart(difficultyStats: List<com.exammaster.data.database.dao.DifficultyStatistic>) {
    if (difficultyStats.isEmpty()) {
        EmptyChartPlaceholder("暂无数据")
        return    }
    
    val chartEntryProducer = remember { ChartEntryModelProducer() }
    
    LaunchedEffect(difficultyStats) {
        val entries = difficultyStats.mapIndexed { index, stat ->
            FloatEntry(index.toFloat(), stat.accuracy.toFloat())
        }
        chartEntryProducer.setEntries(entries)
    }
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
    ) {
        Chart(
            chart = columnChart(),
            chartModelProducer = chartEntryProducer,
            startAxis = startAxis(),
            bottomAxis = bottomAxis()
        )
    }
}

// Placeholder Components - 占位符组件

@Composable
private fun EmptyChartPlaceholder(message: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.BarChart,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = message,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun EmptyHistoryPlaceholder() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(120.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.History,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "暂无答题历史",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun LoadingPlaceholder() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(80.dp),
            contentAlignment = Alignment.Center
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    strokeWidth = 2.dp
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "加载中...",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}