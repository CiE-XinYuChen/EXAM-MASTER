package com.exammaster.data.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import com.exammaster.data.models.AppIcon
import com.exammaster.data.models.Settings
import com.exammaster.data.models.ThemeColor
import com.exammaster.data.models.ThemeMode
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

// 使用统一的DataStore定义
import com.exammaster.data.datastore.dataStore

@Singleton
class PreferencesDataStore @Inject constructor(
    private val context: Context
) {
    companion object {
        private val THEME_MODE = stringPreferencesKey("theme_mode")
        private val THEME_COLOR = stringPreferencesKey("theme_color")
        private val APP_ICON = stringPreferencesKey("app_icon")
        private val NOTIFICATIONS_ENABLED = booleanPreferencesKey("notifications_enabled")
        private val SOUND_ENABLED = booleanPreferencesKey("sound_enabled")
        private val VIBRATION_ENABLED = booleanPreferencesKey("vibration_enabled")
        private val AUTO_SUBMIT_TIMED = booleanPreferencesKey("auto_submit_timed")
        private val DEFAULT_QUESTION_COUNT = intPreferencesKey("default_question_count")
        private val SHOW_CORRECT_ANSWER = booleanPreferencesKey("show_correct_answer")
        private val ENABLE_PROGRESS_TRACKING = booleanPreferencesKey("enable_progress_tracking")
        private val AUTO_SAVE_PROGRESS = booleanPreferencesKey("auto_save_progress")
        private val ENABLE_STATISTICS = booleanPreferencesKey("enable_statistics")
        private val REMINDER_INTERVAL = intPreferencesKey("reminder_interval")
        private val AUTO_NEXT_ON_CORRECT = booleanPreferencesKey("auto_next_on_correct")
    }

    val settingsFlow: Flow<Settings> = context.dataStore.data
        .catch { exception ->
            // 处理读取错误，发出默认设置
            emit(emptyPreferences())
        }
        .map { preferences ->
            Settings(
                themeMode = ThemeMode.valueOf(
                    preferences[THEME_MODE] ?: ThemeMode.SYSTEM.name
                ),
                themeColor = preferences[THEME_COLOR]?.let { ThemeColor.valueOf(it) } ?: ThemeColor.DEFAULT,
                appIcon = preferences[APP_ICON]?.let { AppIcon.valueOf(it) } ?: AppIcon.DEFAULT,
                notificationsEnabled = preferences[NOTIFICATIONS_ENABLED] ?: true,
                soundEnabled = preferences[SOUND_ENABLED] ?: true,
                vibrationEnabled = preferences[VIBRATION_ENABLED] ?: true,
                autoSubmitTimed = preferences[AUTO_SUBMIT_TIMED] ?: true,
                defaultQuestionCount = preferences[DEFAULT_QUESTION_COUNT] ?: 20,
                showCorrectAnswer = preferences[SHOW_CORRECT_ANSWER] ?: true,
                enableProgressTracking = preferences[ENABLE_PROGRESS_TRACKING] ?: true,
                autoSaveProgress = preferences[AUTO_SAVE_PROGRESS] ?: true,
                enableStatistics = preferences[ENABLE_STATISTICS] ?: true,
                reminderInterval = preferences[REMINDER_INTERVAL] ?: 24,
                autoNextOnCorrect = preferences[AUTO_NEXT_ON_CORRECT] ?: true
            )
        }

    suspend fun updateThemeMode(themeMode: ThemeMode) {
        context.dataStore.edit { preferences ->
            preferences[THEME_MODE] = themeMode.name
        }
    }
    
    suspend fun updateThemeColor(themeColor: ThemeColor) {
        context.dataStore.edit { preferences ->
            preferences[THEME_COLOR] = themeColor.name
        }
    }
    
    suspend fun updateAppIcon(appIcon: AppIcon) {
        context.dataStore.edit { preferences ->
            preferences[APP_ICON] = appIcon.name
        }
    }

    suspend fun updateNotificationsEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[NOTIFICATIONS_ENABLED] = enabled
        }
    }

    suspend fun updateSoundEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[SOUND_ENABLED] = enabled
        }
    }

    suspend fun updateVibrationEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[VIBRATION_ENABLED] = enabled
        }
    }

    suspend fun updateAutoSubmitTimed(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[AUTO_SUBMIT_TIMED] = enabled
        }
    }

    suspend fun updateDefaultQuestionCount(count: Int) {
        context.dataStore.edit { preferences ->
            preferences[DEFAULT_QUESTION_COUNT] = count
        }
    }

    suspend fun updateShowCorrectAnswer(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[SHOW_CORRECT_ANSWER] = enabled
        }
    }

    suspend fun updateEnableProgressTracking(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[ENABLE_PROGRESS_TRACKING] = enabled
        }
    }

    suspend fun updateAutoSaveProgress(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[AUTO_SAVE_PROGRESS] = enabled
        }
    }

    suspend fun updateEnableStatistics(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[ENABLE_STATISTICS] = enabled
        }
    }

    suspend fun updateReminderInterval(hours: Int) {
        context.dataStore.edit { preferences ->
            preferences[REMINDER_INTERVAL] = hours
        }
    }

    suspend fun updateAutoNextOnCorrect(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[AUTO_NEXT_ON_CORRECT] = enabled
        }
    }

    suspend fun clearAllData() {
        context.dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
