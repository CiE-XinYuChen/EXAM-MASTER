package com.exammaster.data.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "favorites")
data class Favorite(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val questionId: String,
    val tag: String = "",
    val createdAt: String = System.currentTimeMillis().toString()
)