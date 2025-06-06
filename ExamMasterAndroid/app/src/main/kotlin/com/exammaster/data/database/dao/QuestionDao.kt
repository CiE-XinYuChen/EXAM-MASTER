package com.exammaster.data.database.dao

import androidx.room.*
import com.exammaster.data.database.entities.Question
import kotlinx.coroutines.flow.Flow

@Dao
interface QuestionDao {
    @Query("SELECT * FROM questions")
    fun getAllQuestions(): Flow<List<Question>>

    @Query("SELECT * FROM questions WHERE id = :id")
    suspend fun getQuestionById(id: String): Question?

    @Query("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    suspend fun getRandomQuestion(): Question?

    @Query("""
        SELECT * FROM questions 
        WHERE id NOT IN (SELECT questionId FROM history) 
        ORDER BY RANDOM() LIMIT 1
    """)
    suspend fun getRandomUncompletedQuestion(): Question?

    @Query("""
        SELECT * FROM questions 
        WHERE stem LIKE :query 
        OR options LIKE :query 
        OR id LIKE :query 
        OR qtype LIKE :query 
        OR difficulty LIKE :query
    """)
    suspend fun searchQuestions(query: String): List<Question>

    @Query("SELECT * FROM questions WHERE category = :category")
    suspend fun getQuestionsByCategory(category: String): List<Question>

    @Query("SELECT * FROM questions WHERE difficulty = :difficulty")
    suspend fun getQuestionsByDifficulty(difficulty: String): List<Question>

    @Query("SELECT * FROM questions WHERE category = :category AND difficulty = :difficulty")
    suspend fun getQuestionsByCategoryAndDifficulty(category: String, difficulty: String): List<Question>

    @Query("SELECT DISTINCT category FROM questions WHERE category IS NOT NULL AND category != ''")
    suspend fun getAllCategories(): List<String>

    @Query("SELECT DISTINCT difficulty FROM questions WHERE difficulty IS NOT NULL AND difficulty != ''")
    suspend fun getAllDifficulties(): List<String>

    @Query("SELECT COUNT(*) FROM questions")
    suspend fun getQuestionCount(): Int

    @Query("SELECT * FROM questions ORDER BY CAST(id AS INTEGER) ASC")
    suspend fun getQuestionsInSequence(): List<Question>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuestion(question: Question)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuestions(questions: List<Question>)

    @Delete
    suspend fun deleteQuestion(question: Question)

    @Query("DELETE FROM questions")
    suspend fun deleteAllQuestions()
}