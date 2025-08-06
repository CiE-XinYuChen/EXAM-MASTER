package com.exammaster.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.exammaster.ui.viewmodel.ExamViewModel
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    navController: NavController,
    viewModel: ExamViewModel
) {
    var searchQuery by remember { mutableStateOf("") }
    val searchResults = remember { mutableStateOf<List<com.exammaster.data.database.entities.Question>>(emptyList()) }
    val keyboardController = LocalSoftwareKeyboardController.current
    val coroutineScope = rememberCoroutineScope()
    
    // 添加过滤器状态
    var selectedType by remember { mutableStateOf<String?>(null) }
    var selectedDifficulty by remember { mutableStateOf<String?>(null) }
    var showFilters by remember { mutableStateOf(false) }
    
    // 获取所有题型和难度级别
    val allTypes = remember { mutableStateOf<List<String>>(emptyList()) }
    val allDifficulties = remember { mutableStateOf<List<String>>(emptyList()) }
    
    // 加载题型和难度数据
    LaunchedEffect(Unit) {
        viewModel.getAllQuestionTypes().collect { types ->
            allTypes.value = types
        }
        
        viewModel.getAllDifficulties().collect { difficulties ->
            allDifficulties.value = difficulties
        }
    }
    
    // 搜索和过滤
    fun performSearch() {
        if (searchQuery.isBlank() && selectedType == null && selectedDifficulty == null) {
            searchResults.value = emptyList()
            return
        }
        
        coroutineScope.launch {
            val results = viewModel.searchQuestions(searchQuery).first()
            
            // 应用过滤器
            val filteredResults = results.filter { question ->
                val typeMatch = selectedType == null || question.qtype == selectedType
                val difficultyMatch = selectedDifficulty == null || question.difficulty == selectedDifficulty
                typeMatch && difficultyMatch
            }
            
            searchResults.value = filteredResults
        }
    }
    
    LaunchedEffect(searchQuery, selectedType, selectedDifficulty) {
        performSearch()
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
                text = "搜索题目",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            
            IconButton(onClick = { showFilters = !showFilters }) {
                Icon(
                    imageVector = Icons.Default.FilterList,
                    contentDescription = "过滤器"
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Search Input
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { 
                searchQuery = it
            },
            label = { Text("输入关键词搜索题目") },
            leadingIcon = {
                Icon(Icons.Default.Search, contentDescription = "搜索")
            },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(
                        onClick = { 
                            searchQuery = ""
                            searchResults.value = emptyList()
                        }
                    ) {
                        Icon(Icons.Default.Clear, contentDescription = "清空")
                    }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(
                onSearch = {
                    keyboardController?.hide()
                    performSearch()
                }
            ),
            singleLine = true
        )
        
        // 过滤器
        AnimatedVisibility(visible = showFilters) {
            Column(
                modifier = Modifier.padding(vertical = 8.dp)
            ) {
                Text(
                    text = "题型",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(vertical = 4.dp)
                )
                
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    item {
                        FilterChip(
                            selected = selectedType == null,
                            onClick = { 
                                selectedType = null
                                performSearch()
                            },
                            label = { Text("全部") }
                        )
                    }
                    
                    items(allTypes.value) { type ->
                        FilterChip(
                            selected = selectedType == type,
                            onClick = { 
                                selectedType = if (selectedType == type) null else type
                                performSearch()
                            },
                            label = { Text(type) }
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "难度",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(vertical = 4.dp)
                )
                
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    item {
                        FilterChip(
                            selected = selectedDifficulty == null,
                            onClick = { 
                                selectedDifficulty = null
                                performSearch()
                            },
                            label = { Text("全部") }
                        )
                    }
                    
                    items(allDifficulties.value) { difficulty ->
                        FilterChip(
                            selected = selectedDifficulty == difficulty,
                            onClick = { 
                                selectedDifficulty = if (selectedDifficulty == difficulty) null else difficulty
                                performSearch()
                            },
                            label = { Text(difficulty) }
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Search Results
        when {
            searchQuery.isEmpty() && selectedType == null && selectedDifficulty == null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "输入关键词开始搜索",
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            searchResults.value.isEmpty() -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.SearchOff,
                            contentDescription = null,
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "未找到相关题目",
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            else -> {
                Text(
                    text = "找到 ${searchResults.value.size} 道相关题目",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(searchResults.value) { question ->
                        SearchResultItem(
                            question = question,
                            searchQuery = searchQuery,
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
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SearchResultItem(
    question: com.exammaster.data.database.entities.Question,
    searchQuery: String,
    onQuestionClick: (String) -> Unit
) {
    Card(
        onClick = { onQuestionClick(question.id) },
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
                Text(
                    text = "题目 ${question.id}",
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = "查看题目",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = question.stem,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row {
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
    }
}