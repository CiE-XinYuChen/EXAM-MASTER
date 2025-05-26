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
    suspend fun deleteAllHistory()

    @Query("DELETE FROM history WHERE questionId = :questionId")
    suspend fun deleteHistoryByQuestionId(questionId: String)
}