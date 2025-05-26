package com.exammaster.data.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "history")
data class History(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val questionId: String,
    val userAnswer: String,
    val correct: Boolean,
    val timestamp: String = System.currentTimeMillis().toString()
)