package com.exammaster.data.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

@Entity(tableName = "questions")
data class Question(
    @PrimaryKey
    val id: String,
    val stem: String,
    val answer: String,
    val difficulty: String? = null,
    val qtype: String? = null,
    val category: String? = null,
    val options: String? = null, // JSON string
    val createdAt: String? = null
) {
    fun getOptionsMap(): Map<String, String> {
        return if (options.isNullOrEmpty()) {
            emptyMap()
        } else {
            try {
                val type = object : TypeToken<Map<String, String>>() {}.type
                Gson().fromJson(options, type) ?: emptyMap()
            } catch (e: Exception) {
                emptyMap()
            }
        }
    }

    fun getFormattedOptions(): List<Pair<String, String>> {
        return getOptionsMap().entries.sortedBy { it.key }.map { it.key to it.value }
    }
}