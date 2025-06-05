package com.exammaster.di

import com.exammaster.data.database.dao.*
import com.exammaster.data.repository.ExamRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideExamRepository(
        questionDao: QuestionDao,
        historyDao: HistoryDao,
        favoriteDao: FavoriteDao,
        examSessionDao: ExamSessionDao
    ): ExamRepository {
        return ExamRepository(
            questionDao = questionDao,
            historyDao = historyDao,
            favoriteDao = favoriteDao,
            examSessionDao = examSessionDao
        )
    }
} 