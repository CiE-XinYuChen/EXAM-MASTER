package com.exammaster.data.repository

import com.exammaster.data.datastore.PreferencesDataStore
import com.exammaster.data.models.AppIcon
import com.exammaster.data.models.Settings
import com.exammaster.data.models.ThemeColor
import com.exammaster.data.models.ThemeMode
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SettingsRepository @Inject constructor(
    private val preferencesDataStore: PreferencesDataStore
) {
    /**
     * 获取设置流
     */
    val settingsFlow: Flow<Settings> = preferencesDataStore.settingsFlow

    /**
     * 更新主题模式
     */
    suspend fun updateThemeMode(themeMode: ThemeMode) {
        preferencesDataStore.updateThemeMode(themeMode)
    }
    
    /**
     * 更新主题颜色
     */
    suspend fun updateThemeColor(themeColor: ThemeColor) {
        preferencesDataStore.updateThemeColor(themeColor)
    }
    
    /**
     * 更新应用图标
     */
    suspend fun updateAppIcon(appIcon: AppIcon) {
        preferencesDataStore.updateAppIcon(appIcon)
    }

    /**
     * 更新通知设置
     */
    suspend fun updateNotificationsEnabled(enabled: Boolean) {
        preferencesDataStore.updateNotificationsEnabled(enabled)
    }

    /**
     * 更新声音设置
     */
    suspend fun updateSoundEnabled(enabled: Boolean) {
        preferencesDataStore.updateSoundEnabled(enabled)
    }

    /**
     * 更新震动设置
     */
    suspend fun updateVibrationEnabled(enabled: Boolean) {
        preferencesDataStore.updateVibrationEnabled(enabled)
    }

    /**
     * 更新限时模式自动提交设置
     */
    suspend fun updateAutoSubmitTimed(enabled: Boolean) {
        preferencesDataStore.updateAutoSubmitTimed(enabled)
    }

    /**
     * 更新默认题目数量
     */
    suspend fun updateDefaultQuestionCount(count: Int) {
        preferencesDataStore.updateDefaultQuestionCount(count)
    }

    /**
     * 更新显示正确答案设置
     */
    suspend fun updateShowCorrectAnswer(enabled: Boolean) {
        preferencesDataStore.updateShowCorrectAnswer(enabled)
    }

    /**
     * 更新进度跟踪设置
     */
    suspend fun updateEnableProgressTracking(enabled: Boolean) {
        preferencesDataStore.updateEnableProgressTracking(enabled)
    }

    /**
     * 更新自动保存进度设置
     */
    suspend fun updateAutoSaveProgress(enabled: Boolean) {
        preferencesDataStore.updateAutoSaveProgress(enabled)
    }

    /**
     * 更新统计功能设置
     */
    suspend fun updateEnableStatistics(enabled: Boolean) {
        preferencesDataStore.updateEnableStatistics(enabled)
    }

    /**
     * 更新提醒间隔
     */
    suspend fun updateReminderInterval(hours: Int) {
        preferencesDataStore.updateReminderInterval(hours)
    }

    /**
     * 更新回答正确后自动下一题设置
     */
    suspend fun updateAutoNextOnCorrect(enabled: Boolean) {
        preferencesDataStore.updateAutoNextOnCorrect(enabled)
    }

    /**
     * 清除所有数据
     */
    suspend fun clearAllData() {
        preferencesDataStore.clearAllData()
    }
}
