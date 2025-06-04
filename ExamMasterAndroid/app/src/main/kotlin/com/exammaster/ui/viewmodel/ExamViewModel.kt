package com.exammaster.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.exammaster.data.repository.ExamRepository
import com.exammaster.data.database.entities.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.text.SimpleDateFormat
import java.util.*

class ExamViewModel(private val repository: ExamRepository) : ViewModel() {
    
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
    
    init {
        loadStatistics()
    }
    
    fun loadRandomQuestion() {
        viewModelScope.launch {
            _isLoading.value = true
            val question = repository.getRandomUncompletedQuestion() ?: repository.getRandomQuestion()
            _currentQuestion.value = question
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            _currentMode.value = QuizMode.RANDOM
            _isLoading.value = false
        }
    }
    
    fun loadSequentialQuestion() {
        viewModelScope.launch {
            _isLoading.value = true
            val currentId = _currentQuestion.value?.id
            val question = repository.getNextSequentialQuestion(currentId)
            _currentQuestion.value = question
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            _currentMode.value = QuizMode.SEQUENTIAL
            _isLoading.value = false
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
        val correctAnswer = question.answer.toCharArray().sorted().joinToString("")
        
        val isCorrect = userAnswer == correctAnswer
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
        }
    }
    
    fun nextQuestion() {
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
            _isLoading.value = true
            val wrongQuestions = repository.getWrongQuestions()
            val question = wrongQuestions.randomOrNull()
            _currentQuestion.value = question
            _selectedAnswers.value = emptySet()
            _showResult.value = false
            _currentMode.value = QuizMode.WRONG_ONLY
            _isLoading.value = false
        }
    }
    
    fun loadNextQuestion() {
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
                val correctAnswer = question.answer.toCharArray().sorted().joinToString("")
                val isCorrect = userAnswer.toCharArray().sorted().joinToString("") == correctAnswer
                
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
        if (session != null && session.completed) {
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
                    answers.add(
                        ExamAnswer(
                            questionId = question.id,
                            userAnswer = history.userAnswer,
                            correctAnswer = question.answer,
                            isCorrect = history.correct
                        )
                    )
                }
            }
            
            val startTime = session.startTime.toLongOrNull() ?: 0L
            val endTime = startTime + (session.duration * 1000L) // Approximate end time
            val actualDuration = ((endTime - startTime) / 1000L).toInt()
            
            emit(
                ExamResult(
                    examSessionId = session.id,
                    score = session.score ?: 0f,
                    totalQuestions = questions.size,
                    correctAnswers = answers.count { it.isCorrect },
                    duration = actualDuration,
                    accuracy = session.score ?: 0f,
                    answers = answers
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
    }
      data class Statistics(
        val totalQuestions: Int = 0,
        val answeredQuestions: Int = 0,
        val totalAnswers: Int = 0,
        val correctAnswers: Int = 0,
        val accuracy: Float = 0f
    )
    
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
        val answers: List<ExamAnswer>
    )
    
    data class ExamAnswer(
        val questionId: String,
        val userAnswer: String,
        val correctAnswer: String,
        val isCorrect: Boolean
    )
    
    enum class QuizMode {
        RANDOM, SEQUENTIAL, TIMED, EXAM, WRONG_ONLY
    }
}