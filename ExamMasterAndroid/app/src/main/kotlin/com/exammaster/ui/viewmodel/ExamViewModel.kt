package com.exammaster.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.exammaster.data.repository.ExamRepository
import com.exammaster.data.repository.SettingsRepository
import com.exammaster.data.database.entities.*
import com.exammaster.data.models.Settings
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.text.SimpleDateFormat
import java.util.*
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class ExamViewModel @Inject constructor(
    private val repository: ExamRepository,
    private val settingsRepository: SettingsRepository
) : ViewModel() {
    
    private val _currentQuestion = MutableStateFlow<Question?>(null)
    val currentQuestion: StateFlow<Question?> = _currentQuestion.asStateFlow()
    
    private val _selectedAnswers = MutableStateFlow<Set<String>>(emptySet())
    val selectedAnswers: StateFlow<Set<String>> = _selectedAnswers.asStateFlow()
    
    private val _showResult = MutableStateFlow(false)
    val showResult: StateFlow<Boolean> = _showResult.asStateFlow()
    
    private val _isAnswerCorrect = MutableStateFlow(false)
    val isAnswerCorrect: StateFlow<Boolean> = _isAnswerCorrect.asStateFlow()
    
    private val _statistics = MutableStateFlow(Statistics())
    val statistics: StateFlow<Statistics> = _statistics.asStateFlow()
    
    private val _currentMode = MutableStateFlow(QuizMode.RANDOM)
    val currentMode: StateFlow<QuizMode> = _currentMode.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
      private val _lastBrowsedQuestionId = MutableStateFlow<String?>(null)
    val lastBrowsedQuestionId: StateFlow<String?> = _lastBrowsedQuestionId.asStateFlow()
    
    // Exam Mode States
    private val _currentExamSession = MutableStateFlow<ExamSession?>(null)
    val currentExamSession: StateFlow<ExamSession?> = _currentExamSession.asStateFlow()
    
    private val _unfinishedExamSession = MutableStateFlow<ExamSession?>(null)
    val unfinishedExamSession: StateFlow<ExamSession?> = _unfinishedExamSession.asStateFlow()
    
    private val _examProgress = MutableStateFlow(ExamProgress())
    val examProgress: StateFlow<ExamProgress> = _examProgress.asStateFlow()
    
    private val _examQuestions = MutableStateFlow<List<Question>>(emptyList())
    val examQuestions: StateFlow<List<Question>> = _examQuestions.asStateFlow()
    
    private val _examAnswers = MutableStateFlow<Map<String, String>>(emptyMap())
    val examAnswers: StateFlow<Map<String, String>> = _examAnswers.asStateFlow()
    
    private val _showSubmitDialog = MutableStateFlow(false)
    val showSubmitDialog: StateFlow<Boolean> = _showSubmitDialog.asStateFlow()
    
    val allQuestions = repository.getAllQuestions().stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
    
    val allHistory = repository.getAllHistory().stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
      val allFavorites = repository.getAllFavorites().stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
    
    val recentExamSessions = repository.getAllExamSessions().stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
    
    private val _settings = MutableStateFlow(Settings())
    val settings: StateFlow<Settings> = _settings.asStateFlow()
    
    // 跟踪最近加载的题目ID，避免短时间内重复出现相同题目
    private val recentlyLoadedQuestionIds = mutableSetOf<String>()
    private val MAX_RECENT_QUESTIONS = 5 // 跟踪最近的5道题
    
    init {
        loadStatistics()
        // 观察设置变化
        viewModelScope.launch {
            settingsRepository.settingsFlow.collect { settings ->
                _settings.value = settings
            }
        }
    }
    
    fun loadRandomQuestion() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                
                // 获取所有题目的数量
                val totalQuestions = repository.getQuestionCount()
                
                // 如果题库太小或为空，直接返回随机题目
                if (totalQuestions <= MAX_RECENT_QUESTIONS) {
                    val question = repository.getRandomQuestion()
                    _currentQuestion.value = question
                    _selectedAnswers.value = emptySet()
                    _showResult.value = false
                    _currentMode.value = QuizMode.RANDOM
                    _isLoading.value = false
                    return@launch
                }
                
                // 尝试获取未完成且未在最近列表中的题目
                var attempts = 0
                var question: Question? = null
                
                // 最多尝试5次获取不在最近列表中的题目
                while (attempts < 5) {
                    question = repository.getRandomUncompletedQuestion() ?: repository.getRandomQuestion()
                    
                    // 如果获取到的题目不在最近列表中或是唯一可用的题目，则使用它
                    if (question != null && (!recentlyLoadedQuestionIds.contains(question.id) || attempts >= 3)) {
                        break
                    }
                    attempts++
                }
                
                // 设置当前题目
                if (question != null) {
                    // 更新最近加载的题目ID列表
                    if (recentlyLoadedQuestionIds.size >= MAX_RECENT_QUESTIONS) {
                        // 如果列表已满，移除最早添加的ID
                        recentlyLoadedQuestionIds.iterator().next().let {
                            recentlyLoadedQuestionIds.remove(it)
                        }
                    }
                    // 添加当前题目ID
                    recentlyLoadedQuestionIds.add(question.id)
                    
                    // 设置当前题目
                    _currentQuestion.value = question
                    _selectedAnswers.value = emptySet()
                    _showResult.value = false
                    _currentMode.value = QuizMode.RANDOM
                }
            } catch (e: Exception) {
                android.util.Log.e("ExamViewModel", "Error loading random question: ${e.message}")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun loadSequentialQuestion() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val currentId = _currentQuestion.value?.id
                
                // 获取下一个顺序题目
                val question = repository.getNextSequentialQuestion(currentId)
                
                if (question == null) {
                    // 如果没有下一题，则重新从开始位置获取题目
                    val firstQuestion = repository.getSequentialQuestionStartingFrom(null)
                    _currentQuestion.value = firstQuestion
                } else if (question.id == _currentQuestion.value?.id) {
                    // 如果是同一题目（可能是数据库只有一个题目），查看是否有其他可用题目
                    val allQuestions = repository.getAllQuestions().first()
                    if (allQuestions.size > 1) {
                        // 尝试获取非当前题目的其他题目
                        val otherQuestion = allQuestions.filter { it.id != question.id }.randomOrNull()
                        if (otherQuestion != null) {
                            _currentQuestion.value = otherQuestion
                        } else {
                            _currentQuestion.value = question
                        }
                    } else {
                        // 数据库只有一个题目，保持当前题目
                        _currentQuestion.value = question
                    }
                } else {
                    // 更新最近加载的题目列表
                    if (question.id !in recentlyLoadedQuestionIds) {
                        if (recentlyLoadedQuestionIds.size >= MAX_RECENT_QUESTIONS) {
                            // 如果列表已满，移除最早添加的ID
                            recentlyLoadedQuestionIds.iterator().next().let {
                                recentlyLoadedQuestionIds.remove(it)
                            }
                        }
                        recentlyLoadedQuestionIds.add(question.id)
                    }
                    
                    // 设置当前题目
                    _currentQuestion.value = question
                }
                
                _selectedAnswers.value = emptySet()
                _showResult.value = false
                _currentMode.value = QuizMode.SEQUENTIAL
            } catch (e: Exception) {
                android.util.Log.e("ExamViewModel", "Error loading sequential question: ${e.message}")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun startSequentialFromLastBrowsed() {
        viewModelScope.launch {
            _isLoading.value = true
            val startFromId = _lastBrowsedQuestionId.value
            val question = repository.getSequentialQuestionStartingFrom(startFromId)
            _currentQuestion.value = question
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            _currentMode.value = QuizMode.SEQUENTIAL
            _isLoading.value = false
        }
    }
    
    fun loadQuestionById(id: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val question = repository.getQuestionById(id)
            _currentQuestion.value = question
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            // Update last browsed question ID
            _lastBrowsedQuestionId.value = id
            _isLoading.value = false
        }
    }
      fun selectAnswer(option: String) {
        val question = _currentQuestion.value
        
        // 判断题和单选题只能选一个选项
        if (question?.qtype == "判断题" || question?.qtype == "单选题") {
            _selectedAnswers.value = setOf(option)
            return
        }
        
        // 多选题可以多选
        val currentAnswers = _selectedAnswers.value.toMutableSet()
        if (currentAnswers.contains(option)) {
            currentAnswers.remove(option)
        } else {
            currentAnswers.add(option)
        }
        _selectedAnswers.value = currentAnswers
    }
      fun submitAnswer() {
        val question = _currentQuestion.value ?: return
        val userAnswer = _selectedAnswers.value.sorted().joinToString("")
        
        // 判断题特殊处理：因为选项固定为 A-正确，B-错误
        val isCorrect = if (question.qtype == "判断题") {
            isJudgmentAnswerCorrect(userAnswer, question.answer)
        } else {
            // 非判断题保持原有逻辑
            val correctAnswer = question.answer.toCharArray().sorted().joinToString("")
            userAnswer == correctAnswer
        }
        
        _isAnswerCorrect.value = isCorrect
        _showResult.value = true
        
        // Save to history
        viewModelScope.launch {
            val history = History(
                questionId = question.id,
                userAnswer = userAnswer,
                correct = isCorrect
            )
            repository.insertHistory(history)
            loadStatistics()

            // 如果答案正确且启用了自动下一题，则自动跳转
            if (isCorrect && _settings.value.autoNextOnCorrect) {
                // 延迟一小段时间后跳转，让用户看到正确提示
                kotlinx.coroutines.delay(800)
                nextQuestion()
            }
        }
    }
    
    /**
     * 判断题答案处理辅助函数
     * 将用户选择的A/B选项转换为"正确"/"错误"并与标准答案比较
     */
    private fun isJudgmentAnswerCorrect(userAnswer: String, correctAnswer: String): Boolean {
        // 将 A/B 选项映射到 "正确"/"错误" 再与答案比较
        val mappedAnswer = when (userAnswer) {
            "A" -> "正确"
            "B" -> "错误"
            else -> ""
        }
        return mappedAnswer == correctAnswer
    }
    
    fun nextQuestion() {
        // 直接加载下一题，不需要先置为null
        when (_currentMode.value) {
            QuizMode.RANDOM -> loadRandomQuestion()
            QuizMode.SEQUENTIAL -> loadSequentialQuestion()
            else -> loadRandomQuestion()
        }
    }
    
    fun toggleFavorite() {
        val question = _currentQuestion.value ?: return
        viewModelScope.launch {
            val existing = repository.getFavoriteByQuestionId(question.id)
            if (existing != null) {
                repository.deleteFavoriteByQuestionId(question.id)
            } else {
                val favorite = Favorite(questionId = question.id)
                repository.insertFavorite(favorite)
            }
        }
    }
    
    fun isFavorite(questionId: String): Flow<Boolean> = flow {
        emit(repository.isFavorite(questionId))
    }
    
    fun searchQuestions(query: String): Flow<List<Question>> = flow {
        emit(repository.searchQuestions(query))
    }
    
    fun getWrongQuestions(): Flow<List<Question>> = flow {
        emit(repository.getWrongQuestions())
    }
    
    fun getFavoriteQuestions(): Flow<List<Question>> = flow {
        emit(repository.getFavoriteQuestions())
    }
    
    fun resetHistory() {
        viewModelScope.launch {
            repository.deleteAllHistory()
            loadStatistics()
        }
    }
      fun clearAllUserData() {
        viewModelScope.launch {
            repository.clearAllUserData()
            loadStatistics()
            // Reset current states
            _currentQuestion.value = null
            _selectedAnswers.value = emptySet()
            _showResult.value = false
        }
    }
    
    // Practice Mode Functions
    fun startPracticeMode(mode: QuizMode) {
        _currentMode.value = mode
        when (mode) {
            QuizMode.RANDOM -> loadRandomQuestion()
            QuizMode.SEQUENTIAL -> loadSequentialQuestion()
            QuizMode.WRONG_ONLY -> loadWrongQuestion()
            else -> loadRandomQuestion()
        }
    }
    
    fun loadWrongQuestion() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val wrongQuestions = repository.getWrongQuestions()
                
                if (wrongQuestions.isEmpty()) {
                    // 如果没有错误的题目，设置为null
                    _currentQuestion.value = null
                    _selectedAnswers.value = emptySet()
                    _showResult.value = false
                    _currentMode.value = QuizMode.WRONG_ONLY
                    _isLoading.value = false
                    return@launch
                }
                
                // 过滤掉最近已加载的题目
                val availableQuestions = wrongQuestions.filter { !recentlyLoadedQuestionIds.contains(it.id) }
                
                // 如果过滤后没有可用题目，则使用所有错题
                val questionPool = if (availableQuestions.isEmpty()) wrongQuestions else availableQuestions
                
                // 随机选择一个题目
                val question = questionPool.random()
                
                // 更新最近加载的题目列表
                if (recentlyLoadedQuestionIds.size >= MAX_RECENT_QUESTIONS) {
                    // 如果列表已满，移除最早添加的ID
                    recentlyLoadedQuestionIds.iterator().next().let {
                        recentlyLoadedQuestionIds.remove(it)
                    }
                }
                recentlyLoadedQuestionIds.add(question.id)
                
                _currentQuestion.value = question
                _selectedAnswers.value = emptySet()
                _showResult.value = false
                _currentMode.value = QuizMode.WRONG_ONLY
            } catch (e: Exception) {
                android.util.Log.e("ExamViewModel", "Error loading wrong question: ${e.message}")
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun loadNextQuestion() {
        // 直接加载下一题，不需要先置为null
        when (_currentMode.value) {
            QuizMode.RANDOM -> loadRandomQuestion()
            QuizMode.SEQUENTIAL -> loadSequentialQuestion()
            QuizMode.WRONG_ONLY -> loadWrongQuestion()
            QuizMode.TIMED, QuizMode.EXAM -> nextExamQuestion()
            else -> loadRandomQuestion()
        }
    }
    
    // Exam Mode Functions
    fun startExam(examType: com.exammaster.ui.screens.ExamType, duration: Int, questionCount: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            
            // Get random questions for exam
            val allQuestions = repository.getAllQuestions().first()
            val selectedQuestions = allQuestions.shuffled().take(questionCount)
            
            if (selectedQuestions.isEmpty()) {
                _isLoading.value = false
                return@launch
            }
            
            // Create exam session
            val examSession = ExamSession(
                mode = examType.name,
                questionIds = Gson().toJson(selectedQuestions.map { it.id }),
                startTime = System.currentTimeMillis().toString(),
                duration = duration,
                completed = false
            )
            
            val sessionId = repository.insertExamSession(examSession)
            val updatedSession = examSession.copy(id = sessionId.toInt())
            
            _currentExamSession.value = updatedSession
            _examQuestions.value = selectedQuestions
            _examAnswers.value = emptyMap()
            _examProgress.value = ExamProgress(
                currentIndex = 0,
                totalQuestions = selectedQuestions.size,
                answeredQuestions = 0
            )
            
            // Load first question
            _currentQuestion.value = selectedQuestions.firstOrNull()
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            _currentMode.value = if (examType == com.exammaster.ui.screens.ExamType.TIMED) QuizMode.TIMED else QuizMode.EXAM
            
            _isLoading.value = false
        }
    }
    
    fun nextExamQuestion() {
        val progress = _examProgress.value
        val questions = _examQuestions.value
        
        if (progress.currentIndex < questions.size - 1) {
            // Save current answer if any
            saveCurrentExamAnswer()
            
            // Move to next question
            val newIndex = progress.currentIndex + 1
            _examProgress.value = progress.copy(
                currentIndex = newIndex,
                answeredQuestions = _examAnswers.value.size
            )
            
            _currentQuestion.value = questions[newIndex]
            
            // Load previous answer if exists
            val questionId = questions[newIndex].id
            val previousAnswer = _examAnswers.value[questionId]
            _selectedAnswers.value = if (previousAnswer != null) {
                previousAnswer.toCharArray().toSet().map { it.toString() }.toSet()
            } else {
                emptySet()
            }
        }
    }
    
    fun previousExamQuestion() {
        val progress = _examProgress.value
        val questions = _examQuestions.value
        
        if (progress.currentIndex > 0) {
            // Save current answer if any
            saveCurrentExamAnswer()
            
            // Move to previous question
            val newIndex = progress.currentIndex - 1
            _examProgress.value = progress.copy(
                currentIndex = newIndex,
                answeredQuestions = _examAnswers.value.size
            )
            
            _currentQuestion.value = questions[newIndex]
            
            // Load previous answer if exists
            val questionId = questions[newIndex].id
            val previousAnswer = _examAnswers.value[questionId]
            _selectedAnswers.value = if (previousAnswer != null) {
                previousAnswer.toCharArray().toSet().map { it.toString() }.toSet()
            } else {
                emptySet()
            }
        }
    }
    
    private fun saveCurrentExamAnswer() {
        val currentQuestion = _currentQuestion.value ?: return
        val userAnswer = _selectedAnswers.value.sorted().joinToString("")
        
        if (userAnswer.isNotEmpty()) {
            val updatedAnswers = _examAnswers.value.toMutableMap()
            updatedAnswers[currentQuestion.id] = userAnswer
            _examAnswers.value = updatedAnswers
            
            // Update progress
            _examProgress.value = _examProgress.value.copy(
                answeredQuestions = updatedAnswers.size
            )
        }
    }
    
    fun showSubmitExamDialog() {
        _showSubmitDialog.value = true
    }
    
    fun hideSubmitExamDialog() {
        _showSubmitDialog.value = false
    }
    
    fun submitExam() {
        viewModelScope.launch {
            val session = _currentExamSession.value ?: return@launch
            val questions = _examQuestions.value
            val answers = _examAnswers.value
            
            // Save current answer
            saveCurrentExamAnswer()
            
            // Calculate score
            var correctAnswers = 0
            val finalAnswers = _examAnswers.value
            
            questions.forEach { question ->
                val userAnswer = finalAnswers[question.id] ?: ""
                
                // 判断题特殊处理
                val isCorrect = if (question.qtype == "判断题") {
                    isJudgmentAnswerCorrect(userAnswer, question.answer)
                } else {
                    // 非判断题保持原有逻辑
                    val correctAnswer = question.answer.toCharArray().sorted().joinToString("")
                    userAnswer.toCharArray().sorted().joinToString("") == correctAnswer
                }
                
                if (isCorrect) {
                    correctAnswers++
                }
                
                // Save to history
                val history = History(
                    questionId = question.id,
                    userAnswer = userAnswer,
                    correct = isCorrect
                )
                repository.insertHistory(history)
            }
            
            val score = correctAnswers.toFloat() / questions.size.toFloat()
            
            // Update exam session
            val updatedSession = session.copy(
                completed = true,
                score = score
            )
            repository.updateExamSession(updatedSession)
            _currentExamSession.value = updatedSession
            
            loadStatistics()
        }
    }
    
    fun pauseExam() {
        // Save current answer and exam state
        saveCurrentExamAnswer()
        // The exam session remains in database and can be resumed later
    }
      fun getExamResult(examSessionId: Int): Flow<ExamResult?> = flow {
        val session = repository.getExamSessionById(examSessionId)
        if (session != null) {
            val questionIds: List<String> = try {
                val type = object : TypeToken<List<String>>() {}.type
                Gson().fromJson(session.questionIds, type) ?: emptyList()
            } catch (e: Exception) {
                emptyList()
            }
            
            val questions = questionIds.mapNotNull { repository.getQuestionById(it) }
            val answers = mutableListOf<ExamAnswer>()
            
            questions.forEach { question ->
                val history = repository.getHistoryByQuestionId(question.id).lastOrNull()
                if (history != null) {
                    // 判断题特殊处理
                    val isCorrect = if (question.qtype == "判断题") {
                        isJudgmentAnswerCorrect(history.userAnswer, question.answer)
                    } else {
                        // 非判断题保持原有逻辑
                        history.correct
                    }
                    
                    answers.add(
                        ExamAnswer(
                            questionId = question.id,
                            userAnswer = history.userAnswer,
                            correctAnswer = question.answer,
                            isCorrect = isCorrect,
                            questionType = question.qtype ?: ""
                        )
                    )
                }
            }
            
            val startTime = session.startTime.toLongOrNull() ?: 0L
            val endTime = if (session.completed) {
                startTime + (session.duration * 1000L) // 已完成考试，使用近似结束时间
            } else {
                System.currentTimeMillis() // 未完成考试，使用当前时间
            }
            val actualDuration = ((endTime - startTime) / 1000L).toInt()
            
            emit(
                ExamResult(
                    examSessionId = session.id,
                    score = session.score ?: 0f,
                    totalQuestions = questions.size,
                    correctAnswers = answers.count { it.isCorrect },
                    duration = actualDuration,
                    accuracy = session.score ?: 0f,
                    answers = answers,
                    completed = session.completed,
                    startTime = session.startTime
                )
            )
        } else {
            emit(null)
        }
    }
    
    fun loadExamResult(examSessionId: Int) {
        // This function can be used to preload exam result if needed
        viewModelScope.launch {
            _isLoading.value = true
            // The actual loading is handled by getExamResult flow
            _isLoading.value = false
        }
    }
    
    fun reviewWrongAnswers(examSessionId: Int) {
        viewModelScope.launch {
            _currentMode.value = QuizMode.WRONG_ONLY
            loadWrongQuestion()
        }
    }
    
    fun shareExamResult(result: ExamResult) {
        // This would typically use Android's share intent
        // Implementation would depend on the specific requirements
    }
    
    private fun loadStatistics() {
        viewModelScope.launch {
            val totalQuestions = repository.getQuestionCount()
            val answeredQuestions = repository.getAnsweredQuestionCount()
            val totalAnswers = repository.getTotalAnswerCount()
            val correctAnswers = repository.getCorrectAnswerCount()
            
            val accuracy = if (totalAnswers > 0) {
                (correctAnswers.toFloat() / totalAnswers.toFloat()) * 100f
            } else 0f
            
            _statistics.value = Statistics(
                totalQuestions = totalQuestions,
                answeredQuestions = answeredQuestions,
                totalAnswers = totalAnswers,
                correctAnswers = correctAnswers,
                accuracy = accuracy
            )
        }
    }    data class Statistics(
        val totalQuestions: Int = 0,
        val answeredQuestions: Int = 0,
        val totalAnswers: Int = 0,
        val correctAnswers: Int = 0,
        val accuracy: Float = 0f
    )
    
    data class AdvancedStatistics(
        val dailyStats: List<com.exammaster.data.database.dao.DailyStatistic> = emptyList(),
        val categoryStats: List<com.exammaster.data.database.dao.CategoryStatistic> = emptyList(),
        val difficultyStats: List<com.exammaster.data.database.dao.DifficultyStatistic> = emptyList(),
        val weeklyCount: Int = 0,
        val monthlyCount: Int = 0,
        val mostAttempted: List<com.exammaster.data.database.dao.QuestionAttemptStatistic> = emptyList(),
        val recentHistory: List<com.exammaster.data.database.dao.HistoryWithQuestion> = emptyList()
    )
    
    private val _advancedStatistics = MutableStateFlow(AdvancedStatistics())
    val advancedStatistics: StateFlow<AdvancedStatistics> = _advancedStatistics.asStateFlow()
    
    fun loadAdvancedStatistics() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val dailyStats = repository.getDailyStatistics()
                val categoryStats = repository.getCategoryStatistics()
                val difficultyStats = repository.getDifficultyStatistics()
                val weeklyCount = repository.getWeeklyAnswerCount()
                val monthlyCount = repository.getMonthlyAnswerCount()
                val mostAttempted = repository.getMostAttemptedQuestions()
                val recentHistory = repository.getRecentHistory(20)
                
                _advancedStatistics.value = AdvancedStatistics(
                    dailyStats = dailyStats,
                    categoryStats = categoryStats,
                    difficultyStats = difficultyStats,
                    weeklyCount = weeklyCount,
                    monthlyCount = monthlyCount,
                    mostAttempted = mostAttempted,
                    recentHistory = recentHistory
                )
            } catch (e: Exception) {
                // Handle error gracefully
                _advancedStatistics.value = AdvancedStatistics()
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    data class ExamProgress(
        val currentIndex: Int = 0,
        val totalQuestions: Int = 0,
        val answeredQuestions: Int = 0
    )
      data class ExamResult(
        val examSessionId: Int,
        val score: Float,
        val totalQuestions: Int,
        val correctAnswers: Int,
        val duration: Int, // in seconds
        val accuracy: Float,
        val answers: List<ExamAnswer>,
        val completed: Boolean = true,
        val startTime: String = ""
    )
    
    data class ExamAnswer(
        val questionId: String,
        val userAnswer: String,
        val correctAnswer: String,
        val isCorrect: Boolean,
        val questionType: String
    )
    
    enum class QuizMode {
        RANDOM, SEQUENTIAL, TIMED, EXAM, WRONG_ONLY
    }
    
    fun checkUnfinishedExam() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val unfinished = repository.getCurrentExamSession()
                _unfinishedExamSession.value = unfinished
            } catch (e: Exception) {
                // 处理可能的异常
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun resumeExam(examId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                val session = repository.getExamSessionById(examId)
                if (session != null && !session.completed) {
                    _currentExamSession.value = session
                    
                    // 加载试题
                    val questionIds: List<String> = try {
                        val type = object : TypeToken<List<String>>() {}.type
                        Gson().fromJson(session.questionIds, type) ?: emptyList()
                    } catch (e: Exception) {
                        emptyList()
                    }
                    
                    val questions = questionIds.mapNotNull { repository.getQuestionById(it) }
                    _examQuestions.value = questions
                      // 加载已回答的答案
                    val answers = mutableMapOf<String, String>()
                    var answeredCount = 0
                    
                    questions.forEach { question ->
                        val history = repository.getHistoryByQuestionId(question.id).lastOrNull()
                        if (history != null && history.userAnswer.isNotEmpty()) {
                            answers[question.id] = history.userAnswer
                            answeredCount++
                        }
                    }
                    
                    _examAnswers.value = answers
                    
                    // 设置考试进度
                    _examProgress.value = ExamProgress(
                        currentIndex = 0,
                        totalQuestions = questions.size,
                        answeredQuestions = answeredCount
                    )
                    
                    // 加载第一道题
                    _currentQuestion.value = questions.firstOrNull()
                    _selectedAnswers.value = emptySet()
                    _showResult.value = false
                    _currentMode.value = if (session.mode == "TIMED") QuizMode.TIMED else QuizMode.EXAM
                }
            } catch (e: Exception) {
                // 处理可能的异常
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun abandonExam(examId: Int) {
        viewModelScope.launch {
            try {
                val session = repository.getExamSessionById(examId)
                if (session != null) {
                    // 标记考试已完成但分数为0
                    val updatedSession = session.copy(completed = true, score = 0f)
                    repository.updateExamSession(updatedSession)
                    _unfinishedExamSession.value = null
                }
            } catch (e: Exception) {
                // 处理可能的异常
            }
        }
    }
    
    // 获取所有题型
    fun getAllQuestionTypes(): Flow<List<String>> = flow {
        val types = repository.getAllQuestions().first()
            .mapNotNull { it.qtype }
            .distinct()
            .sorted()
        emit(types)
    }
    
    // 获取所有难度级别
    fun getAllDifficulties(): Flow<List<String>> = flow {
        emit(repository.getAllDifficulties())
    }
}