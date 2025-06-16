package com.exammaster.data.repository

import com.exammaster.data.database.dao.*
import com.exammaster.data.database.entities.*
import kotlinx.coroutines.flow.Flow

class ExamRepository(
    private val questionDao: QuestionDao,
    private val historyDao: HistoryDao,
    private val favoriteDao: FavoriteDao,
    private val examSessionDao: ExamSessionDao
) {
    // Question operations
    fun getAllQuestions(): Flow<List<Question>> = questionDao.getAllQuestions()
    
    suspend fun getQuestionById(id: String): Question? = questionDao.getQuestionById(id)
    
    suspend fun getRandomQuestion(): Question? = questionDao.getRandomQuestion()
    
    suspend fun getRandomUncompletedQuestion(): Question? = questionDao.getRandomUncompletedQuestion()
    
    suspend fun searchQuestions(query: String): List<Question> = questionDao.searchQuestions("%$query%")
    
    suspend fun getQuestionsByCategory(category: String): List<Question> = 
        questionDao.getQuestionsByCategory(category)
    
    suspend fun getQuestionsByDifficulty(difficulty: String): List<Question> = 
        questionDao.getQuestionsByDifficulty(difficulty)
    
    suspend fun getQuestionsByCategoryAndDifficulty(category: String, difficulty: String): List<Question> = 
        questionDao.getQuestionsByCategoryAndDifficulty(category, difficulty)
    
    suspend fun getAllCategories(): List<String> = questionDao.getAllCategories()
    
    suspend fun getAllDifficulties(): List<String> = questionDao.getAllDifficulties()
    
    suspend fun getQuestionCount(): Int = questionDao.getQuestionCount()
    
    suspend fun getQuestionsInSequence(): List<Question> = questionDao.getQuestionsInSequence()
    
    suspend fun insertQuestions(questions: List<Question>) = questionDao.insertQuestions(questions)

    // History operations
    fun getAllHistory(): Flow<List<History>> = historyDao.getAllHistory()
    
    suspend fun getHistoryByQuestionId(questionId: String): List<History> = 
        historyDao.getHistoryByQuestionId(questionId)
    
    suspend fun getWrongQuestionIds(): List<String> = historyDao.getWrongQuestionIds()
    
    suspend fun getAnsweredQuestionIds(): List<String> = historyDao.getAnsweredQuestionIds()
    
    suspend fun getAnsweredQuestionCount(): Int = historyDao.getAnsweredQuestionCount()
    
    suspend fun getCorrectAnswerCount(): Int = historyDao.getCorrectAnswerCount()
    
    suspend fun getTotalAnswerCount(): Int = historyDao.getTotalAnswerCount()
    
    suspend fun getQuestionAttemptCount(questionId: String): Int = historyDao.getQuestionAttemptCount(questionId)
    
    suspend fun insertHistory(history: History) = historyDao.insertHistory(history)
    
    suspend fun deleteAllHistory() = historyDao.deleteAllHistory()

    // Favorite operations
    fun getAllFavorites(): Flow<List<Favorite>> = favoriteDao.getAllFavorites()
    
    suspend fun getFavoriteByQuestionId(questionId: String): Favorite? = 
        favoriteDao.getFavoriteByQuestionId(questionId)
    
    suspend fun getFavoriteQuestionIds(): List<String> = favoriteDao.getFavoriteQuestionIds()
    
    suspend fun isFavorite(questionId: String): Boolean = favoriteDao.isFavorite(questionId)
    
    suspend fun insertFavorite(favorite: Favorite) = favoriteDao.insertFavorite(favorite)
    
    suspend fun deleteFavoriteByQuestionId(questionId: String) = 
        favoriteDao.deleteFavoriteByQuestionId(questionId)
    
    suspend fun deleteAllFavorites() = favoriteDao.deleteAllFavorites()
    
    suspend fun updateFavoriteTag(questionId: String, tag: String) = 
        favoriteDao.updateFavoriteTag(questionId, tag)

    // Exam session operations
    fun getAllExamSessions(): Flow<List<ExamSession>> = examSessionDao.getAllExamSessions()
    
    suspend fun getCompletedExamSessions(): List<ExamSession> = examSessionDao.getCompletedExamSessions()
    
    suspend fun getExamSessionById(id: Int): ExamSession? = examSessionDao.getExamSessionById(id)
    
    suspend fun getCurrentExamSession(): ExamSession? = examSessionDao.getCurrentExamSession()
    
    suspend fun insertExamSession(examSession: ExamSession): Long = 
        examSessionDao.insertExamSession(examSession)
      suspend fun updateExamSession(examSession: ExamSession) = examSessionDao.updateExamSession(examSession)
    
    suspend fun completeExamSession(id: Int, score: Float) = 
        examSessionDao.completeExamSession(id, score)

    // Advanced statistics operations
    suspend fun getDailyStatistics() = historyDao.getDailyStatistics()
    
    suspend fun getCategoryStatistics() = historyDao.getCategoryStatistics()
    
    suspend fun getDifficultyStatistics() = historyDao.getDifficultyStatistics()
    
    suspend fun getRecentHistory(limit: Int = 50) = historyDao.getRecentHistory(limit)
    
    suspend fun getWeeklyAnswerCount(): Int {
        val calendar = java.util.Calendar.getInstance()
        calendar.set(java.util.Calendar.DAY_OF_WEEK, calendar.firstDayOfWeek)
        calendar.set(java.util.Calendar.HOUR_OF_DAY, 0)
        calendar.set(java.util.Calendar.MINUTE, 0)
        calendar.set(java.util.Calendar.SECOND, 0)
        calendar.set(java.util.Calendar.MILLISECOND, 0)
        return historyDao.getWeeklyAnswerCount(calendar.timeInMillis)
    }
    
    suspend fun getMonthlyAnswerCount(): Int {
        val calendar = java.util.Calendar.getInstance()
        calendar.set(java.util.Calendar.DAY_OF_MONTH, 1)
        calendar.set(java.util.Calendar.HOUR_OF_DAY, 0)
        calendar.set(java.util.Calendar.MINUTE, 0)
        calendar.set(java.util.Calendar.SECOND, 0)
        calendar.set(java.util.Calendar.MILLISECOND, 0)
        return historyDao.getMonthlyAnswerCount(calendar.timeInMillis)
    }
    
    suspend fun getMostAttemptedQuestions() = historyDao.getMostAttemptedQuestions()

    // Complex operations
    suspend fun getWrongQuestions(): List<Question> {
        val wrongIds = getWrongQuestionIds()
        return wrongIds.mapNotNull { getQuestionById(it) }
    }
    
    suspend fun getFavoriteQuestions(): List<Question> {
        val favoriteIds = getFavoriteQuestionIds()
        return favoriteIds.mapNotNull { getQuestionById(it) }
    }
    
    suspend fun getNextSequentialQuestion(currentQuestionId: String?): Question? {
        val allQuestions = getQuestionsInSequence()
        if (allQuestions.isEmpty()) return null
        
        return if (currentQuestionId == null) {
            allQuestions.first()
        } else {
            val currentIndex = allQuestions.indexOfFirst { it.id == currentQuestionId }
            if (currentIndex >= 0 && currentIndex < allQuestions.size - 1) {
                allQuestions[currentIndex + 1]
            } else {
                allQuestions.first() // Loop back to start
            }
        }
    }
    
    suspend fun getSequentialQuestionStartingFrom(questionId: String?): Question? {
        val allQuestions = getQuestionsInSequence()
        if (allQuestions.isEmpty()) return null
        
        return if (questionId == null) {
            allQuestions.first()
        } else {
            val currentIndex = allQuestions.indexOfFirst { it.id == questionId }
            if (currentIndex >= 0) {
                allQuestions[currentIndex] // Start from the specified question
            } else {
                allQuestions.first() // If not found, start from first
            }
        }    }
    
    suspend fun getRandomQuestions(count: Int): List<Question> {
        val allQuestions = getQuestionsInSequence()
        return allQuestions.shuffled().take(count)
    }
    
    // Clear all user data
    suspend fun clearAllUserData() {
        deleteAllHistory()
        deleteAllFavorites()
        examSessionDao.deleteAllExamSessions()
    }
}