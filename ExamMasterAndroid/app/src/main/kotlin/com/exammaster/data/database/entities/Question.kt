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
        // 如果是判断题，生成固定的选项
        if (qtype == "判断题") {
            return listOf("A" to "正确", "B" to "错误")
        }
        
        return getOptionsMap().entries.sortedBy { it.key }.map { it.key to it.value }
    }
    
    /**
     * 获取格式化后的答案显示内容
     * 特别处理判断题，将选项字母转换为对应的"正确"/"错误"文本
     */
    fun getFormattedAnswer(): String {
        return when {
            qtype == "判断题" -> {
                when (answer) {
                    "A", "正确" -> "正确"
                    "B", "错误" -> "错误"
                    else -> answer
                }
            }
            else -> answer
        }
    }
    
    /**
     * 将用户的选项转换为易读的格式
     * 特别是对于判断题，将A/B转换为"正确"/"错误"
     */
    fun formatUserAnswer(userAnswer: String): String {
        return when {
            qtype == "判断题" -> {
                when (userAnswer) {
                    "A" -> "正确"
                    "B" -> "错误"
                    else -> if (userAnswer.isEmpty()) "未选择" else userAnswer
                }
            }
            else -> if (userAnswer.isEmpty()) "未选择" else userAnswer
        }
    }
}