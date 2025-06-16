package com.exammaster.data.database.dao

import androidx.room.*
import com.exammaster.data.database.entities.History
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {
    @Query("SELECT * FROM history ORDER BY timestamp DESC")
    fun getAllHistory(): Flow<List<History>>

    @Query("SELECT * FROM history WHERE questionId = :questionId ORDER BY timestamp DESC")
    suspend fun getHistoryByQuestionId(questionId: String): List<History>

    @Query("SELECT questionId FROM history WHERE correct = 0")
    suspend fun getWrongQuestionIds(): List<String>

    @Query("SELECT DISTINCT questionId FROM history")
    suspend fun getAnsweredQuestionIds(): List<String>

    @Query("SELECT COUNT(DISTINCT questionId) FROM history")
    suspend fun getAnsweredQuestionCount(): Int

    @Query("SELECT COUNT(*) FROM history WHERE correct = 1")
    suspend fun getCorrectAnswerCount(): Int

    @Query("SELECT COUNT(*) FROM history")
    suspend fun getTotalAnswerCount(): Int

    @Query("SELECT COUNT(*) FROM history WHERE questionId = :questionId")
    suspend fun getQuestionAttemptCount(questionId: String): Int

    @Query("""
        SELECT 
            COUNT(*) as total
        FROM history h 
        JOIN questions q ON h.questionId = q.id
        WHERE q.difficulty = :difficulty
    """)
    suspend fun getTotalByDifficulty(difficulty: String): Int

    @Query("""
        SELECT 
            COUNT(*) as correct_count
        FROM history h 
        JOIN questions q ON h.questionId = q.id
        WHERE q.difficulty = :difficulty AND h.correct = 1
    """)
    suspend fun getCorrectByDifficulty(difficulty: String): Int

    @Query("""
        SELECT 
            COUNT(*) as total
        FROM history h 
        JOIN questions q ON h.questionId = q.id
        WHERE q.category = :category
    """)
    suspend fun getTotalByCategory(category: String): Int

    @Query("""
        SELECT 
            COUNT(*) as correct_count
        FROM history h 
        JOIN questions q ON h.questionId = q.id
        WHERE q.category = :category AND h.correct = 1
    """)
    suspend fun getCorrectByCategory(category: String): Int

    @Insert
    suspend fun insertHistory(history: History)

    @Delete
    suspend fun deleteHistory(history: History)

    @Query("DELETE FROM history")
    suspend fun deleteAllHistory()    @Query("DELETE FROM history WHERE questionId = :questionId")
    suspend fun deleteHistoryByQuestionId(questionId: String)
    
    // Advanced statistics queries
    @Query("""
        SELECT 
            DATE(timestamp/1000, 'unixepoch') as date,
            COUNT(*) as totalAnswers,
            SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correctAnswers
        FROM history 
        GROUP BY DATE(timestamp/1000, 'unixepoch')
        ORDER BY date DESC
        LIMIT 30
    """)
    suspend fun getDailyStatistics(): List<DailyStatistic>
      @Query("""
        SELECT 
            q.category,
            COUNT(*) as totalCount,
            SUM(CASE WHEN h.correct = 1 THEN 1 ELSE 0 END) as correctCount,
            ROUND(CAST(SUM(CASE WHEN h.correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as accuracy
        FROM history h
        JOIN questions q ON h.questionId = q.id
        GROUP BY q.category
    """)
    suspend fun getCategoryStatistics(): List<CategoryStatistic>
      @Query("""
        SELECT 
            q.difficulty,
            COUNT(*) as totalCount,
            SUM(CASE WHEN h.correct = 1 THEN 1 ELSE 0 END) as correctCount,
            ROUND(CAST(SUM(CASE WHEN h.correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as accuracy
        FROM history h
        JOIN questions q ON h.questionId = q.id
        GROUP BY q.difficulty
    """)
    suspend fun getDifficultyStatistics(): List<DifficultyStatistic>
      @Query("""
        SELECT 
            h.id,
            h.questionId,
            h.userAnswer,
            h.correct as isCorrect,
            h.timestamp,
            q.stem as questionContent,
            q.category,
            q.options as optionA,
            '' as optionB,
            '' as optionC,
            '' as optionD,
            q.answer
        FROM history h
        JOIN questions q ON h.questionId = q.id
        ORDER BY h.timestamp DESC
        LIMIT :limit
    """)
    suspend fun getRecentHistory(limit: Int = 50): List<HistoryWithQuestion>
    
    @Query("""
        SELECT 
            COUNT(*) as weeklyCount
        FROM history 
        WHERE timestamp >= :weekStartTimestamp
    """)
    suspend fun getWeeklyAnswerCount(weekStartTimestamp: Long): Int
    
    @Query("""
        SELECT 
            COUNT(*) as monthlyCount
        FROM history 
        WHERE timestamp >= :monthStartTimestamp
    """)
    suspend fun getMonthlyAnswerCount(monthStartTimestamp: Long): Int    @Query("""
        SELECT 
            h.questionId,
            q.stem as questionContent,
            COUNT(*) as attemptCount,
            SUM(CASE WHEN h.correct = 1 THEN 1 ELSE 0 END) as correctCount
        FROM history h
        JOIN questions q ON h.questionId = q.id
        GROUP BY h.questionId
        HAVING attemptCount > 1
        ORDER BY attemptCount DESC
        LIMIT 20
    """)
    suspend fun getMostAttemptedQuestions(): List<QuestionAttemptStatistic>
}

data class DailyStatistic(
    val date: String,
    val totalAnswers: Int,
    val correctAnswers: Int
)

data class CategoryStatistic(
    val category: String,
    val totalCount: Int,
    val correctCount: Int,
    val accuracy: Double
)

data class DifficultyStatistic(
    val difficulty: String,
    val totalCount: Int,
    val correctCount: Int,
    val accuracy: Double
)

data class HistoryWithQuestion(
    val id: Int,
    val questionId: String,
    val userAnswer: String,
    val isCorrect: Boolean,
    val timestamp: String,
    val questionContent: String,
    val category: String?,
    val optionA: String?,
    val optionB: String?,
    val optionC: String?,
    val optionD: String?,
    val answer: String
)

data class QuestionAttemptStatistic(
    val questionId: String,
    val questionContent: String,
    val attemptCount: Int,
    val correctCount: Int
)