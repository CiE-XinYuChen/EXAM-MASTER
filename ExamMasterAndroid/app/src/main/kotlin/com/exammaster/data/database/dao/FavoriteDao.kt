package com.exammaster.data.database.dao

import androidx.room.*
import com.exammaster.data.database.entities.Favorite
import kotlinx.coroutines.flow.Flow

@Dao
interface FavoriteDao {
    @Query("SELECT * FROM favorites ORDER BY createdAt DESC")
    fun getAllFavorites(): Flow<List<Favorite>>

    @Query("SELECT * FROM favorites WHERE questionId = :questionId")
    suspend fun getFavoriteByQuestionId(questionId: String): Favorite?

    @Query("SELECT questionId FROM favorites")
    suspend fun getFavoriteQuestionIds(): List<String>

    @Query("SELECT EXISTS(SELECT 1 FROM favorites WHERE questionId = :questionId)")
    suspend fun isFavorite(questionId: String): Boolean

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFavorite(favorite: Favorite)

    @Delete
    suspend fun deleteFavorite(favorite: Favorite)

    @Query("DELETE FROM favorites WHERE questionId = :questionId")
    suspend fun deleteFavoriteByQuestionId(questionId: String)

    @Query("UPDATE favorites SET tag = :tag WHERE questionId = :questionId")
    suspend fun updateFavoriteTag(questionId: String, tag: String)

    @Query("DELETE FROM favorites")
    suspend fun deleteAllFavorites()
}