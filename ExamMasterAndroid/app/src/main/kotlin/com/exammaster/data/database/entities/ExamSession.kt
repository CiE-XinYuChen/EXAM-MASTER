package com.exammaster.data.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "exam_sessions")
data class ExamSession(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val mode: String, // "timed", "exam", "sequential", "random"
    val questionIds: String, // JSON array of question IDs
    val startTime: String,
    val duration: Int = 0, // seconds, 0 for unlimited
    val completed: Boolean = false,
    val score: Float? = null
)