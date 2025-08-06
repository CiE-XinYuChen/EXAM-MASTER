package com.exammaster.data.database.dao

import androidx.room.*
import com.exammaster.data.database.entities.ExamSession
import kotlinx.coroutines.flow.Flow

@Dao
interface ExamSessionDao {
    @Query("SELECT * FROM exam_sessions ORDER BY startTime DESC")
    fun getAllExamSessions(): Flow<List<ExamSession>>

    @Query("SELECT * FROM exam_sessions WHERE completed = 1 ORDER BY startTime DESC LIMIT 10")
    suspend fun getCompletedExamSessions(): List<ExamSession>

    @Query("SELECT * FROM exam_sessions WHERE id = :id")
    suspend fun getExamSessionById(id: Int): ExamSession?

    @Query("SELECT * FROM exam_sessions WHERE completed = 0 ORDER BY startTime DESC LIMIT 1")
    suspend fun getCurrentExamSession(): ExamSession?

    @Insert
    suspend fun insertExamSession(examSession: ExamSession): Long

    @Update
    suspend fun updateExamSession(examSession: ExamSession)

    @Delete
    suspend fun deleteExamSession(examSession: ExamSession)

    @Query("UPDATE exam_sessions SET completed = 1, score = :score WHERE id = :id")
    suspend fun completeExamSession(id: Int, score: Float)

    @Query("DELETE FROM exam_sessions")
    suspend fun deleteAllExamSessions()
}