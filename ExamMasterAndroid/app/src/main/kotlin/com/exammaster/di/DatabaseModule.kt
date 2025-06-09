package com.exammaster.di

import android.content.Context
import androidx.room.Room
import com.exammaster.data.database.ExamDatabase
import com.exammaster.data.database.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideExamDatabase(@ApplicationContext context: Context): ExamDatabase {
        return Room.databaseBuilder(
            context.applicationContext,
            ExamDatabase::class.java,
            "exam_database"
        ).build()
    }

    @Provides
    fun provideQuestionDao(database: ExamDatabase): QuestionDao {
        return database.questionDao()
    }

    @Provides
    fun provideHistoryDao(database: ExamDatabase): HistoryDao {
        return database.historyDao()
    }

    @Provides
    fun provideFavoriteDao(database: ExamDatabase): FavoriteDao {
        return database.favoriteDao()
    }

    @Provides
    fun provideExamSessionDao(database: ExamDatabase): ExamSessionDao {
        return database.examSessionDao()
    }
}
