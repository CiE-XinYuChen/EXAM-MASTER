package com.exammaster.data.database

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context
import com.exammaster.data.database.entities.*
import com.exammaster.data.database.dao.*

@Database(
    entities = [Question::class, History::class, Favorite::class, ExamSession::class],
    version = 1,
    exportSchema = false
)
abstract class ExamDatabase : RoomDatabase() {
    abstract fun questionDao(): QuestionDao
    abstract fun historyDao(): HistoryDao
    abstract fun favoriteDao(): FavoriteDao
    abstract fun examSessionDao(): ExamSessionDao

    companion object {
        @Volatile
        private var INSTANCE: ExamDatabase? = null

        fun getDatabase(context: Context): ExamDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    ExamDatabase::class.java,
                    "exam_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}