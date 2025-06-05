package com.exammaster.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.exammaster.data.repository.ExamRepository
import com.exammaster.data.database.entities.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

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
    
    enum class QuizMode {
        RANDOM, SEQUENTIAL, TIMED, EXAM, WRONG_ONLY
    }
}