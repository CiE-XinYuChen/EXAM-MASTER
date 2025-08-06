package com.exammaster.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FavoritesScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    val favoriteQuestions = remember { mutableStateOf<List<com.exammaster.data.database.entities.Question>>(emptyList()) }
    
    LaunchedEffect(Unit) {
        viewModel.getFavoriteQuestions().collect { questions ->
            favoriteQuestions.value = questions
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
                text = "收藏题目",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.width(48.dp)) // Balance the layout
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (favoriteQuestions.value.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Default.FavoriteBorder,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "暂无收藏题目",
                        fontSize = 16.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(favoriteQuestions.value) { question ->
                    FavoriteQuestionItem(
                        question = question,
                        viewModel = viewModel,
                        onQuestionClick = { questionId ->
                            viewModel.loadQuestionById(questionId)
                            navController.navigate("question")
                        }
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FavoriteQuestionItem(
    question: com.exammaster.data.database.entities.Question,
    viewModel: ExamViewModel,
    onQuestionClick: (String) -> Unit
) {
    Card(
        onClick = { onQuestionClick(question.id) },
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Favorite,
                contentDescription = "收藏",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(
                modifier = Modifier.weight(1f)
            ) {
                var attemptCount by remember { mutableStateOf(0) }
                
                LaunchedEffect(question.id) {
                    viewModel.getQuestionAttemptCount(question.id).collect { count -> 
                        attemptCount = count 
                    }
                }
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "题目 ${question.id}",
                        fontWeight = FontWeight.Medium
                    )
                    
                    // 作答次数标签
                    if (attemptCount > 0) {
                        Surface(
                            color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.6f),
                            shape = androidx.compose.foundation.shape.RoundedCornerShape(12.dp)
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
                
                Text(
                    text = question.stem,
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.padding(top = 4.dp)
                )
                
                Row(
                    modifier = Modifier.padding(top = 8.dp)
                ) {
                    AssistChip(
                        onClick = { },
                        label = { 
                            Text(
                                text = question.qtype ?: "未知题型",
                                fontSize = 12.sp
                            )
                        },
                        modifier = Modifier.height(24.dp)
                    )
                    
                    Spacer(modifier = Modifier.width(8.dp))
                    
                    AssistChip(
                        onClick = { },
                        label = { 
                            Text(
                                text = "难度: ${question.difficulty ?: "未知"}",
                                fontSize = 12.sp
                            )
                        },
                        modifier = Modifier.height(24.dp)
                    )
                }
            }
            
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "查看题目",
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}