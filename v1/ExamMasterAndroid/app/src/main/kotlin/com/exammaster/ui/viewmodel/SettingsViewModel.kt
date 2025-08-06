package com.exammaster.ui.viewmodel

import android.widget.Toast
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.exammaster.ExamMasterApplication
import com.exammaster.data.models.AppIcon
import com.exammaster.data.models.Settings
import com.exammaster.data.models.ThemeColor
import com.exammaster.data.models.ThemeMode
import com.exammaster.data.repository.SettingsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    private val _settings = MutableStateFlow(Settings())
    val settings: StateFlow<Settings> = _settings.asStateFlow()

    private var hasShownToast = false

    init {
        // 观察设置变化
        viewModelScope.launch {
            settingsRepository.settingsFlow.collect { settings ->
                _settings.value = settings
            }
        }
    }

    fun updateThemeMode(themeMode: ThemeMode) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                settingsRepository.updateThemeMode(themeMode)
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "更新主题失败: ${e.message}"
                )
            }
        }
    }

    fun updateThemeColor(themeColor: ThemeColor) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                settingsRepository.updateThemeColor(themeColor)
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "更新主题颜色失败: ${e.message}"
                )
            }
        }
    }

    fun updateAppIcon(appIcon: AppIcon) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                settingsRepository.updateAppIcon(appIcon)
                val success = changeAppIcon(appIcon)

                if (!hasShownToast) {
                    val app = ExamMasterApplication.getInstance()
                    val toastMessage = if (success) {
                        "图标已更改，重启应用后完全生效"
                    } else {
                        "图标更改失败，请重启应用后重试"
                    }

                    Toast.makeText(app, toastMessage, Toast.LENGTH_LONG).show()
                    hasShownToast = true
                }

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = if (success) null else "图标更改失败，重启应用后可能生效"
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "更新应用图标失败: ${e.message}"
                )
            }
        }
    }

    private fun changeAppIcon(appIcon: AppIcon): Boolean {
        // 调用应用程序类中的图标更换功能
        return try {
            ExamMasterApplication.getInstance().changeAppIcon(appIcon)
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun updateNotificationsEnabled(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateNotificationsEnabled(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新通知设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateSoundEnabled(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateSoundEnabled(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新声音设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateVibrationEnabled(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateVibrationEnabled(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新震动设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateAutoSubmitTimed(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateAutoSubmitTimed(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新自动提交设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateDefaultQuestionCount(count: Int) {
        viewModelScope.launch {
            try {
                settingsRepository.updateDefaultQuestionCount(count)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新默认题目数量失败: ${e.message}"
                )
            }
        }
    }

    fun updateShowCorrectAnswer(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateShowCorrectAnswer(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新答案显示设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateEnableProgressTracking(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateEnableProgressTracking(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新进度跟踪设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateAutoSaveProgress(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateAutoSaveProgress(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新自动保存设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateEnableStatistics(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateEnableStatistics(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新统计设置失败: ${e.message}"
                )
            }
        }
    }

    fun updateReminderInterval(hours: Int) {
        viewModelScope.launch {
            try {
                settingsRepository.updateReminderInterval(hours)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新提醒间隔失败: ${e.message}"
                )
            }
        }
    }

    fun updateAutoNextOnCorrect(enabled: Boolean) {
        viewModelScope.launch {
            try {
                settingsRepository.updateAutoNextOnCorrect(enabled)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    errorMessage = "更新自动下一题设置失败: \\${e.message}"
                )
            }
        }
    }

    fun clearAllData() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                settingsRepository.clearAllData()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    showClearDataSuccess = true
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "清除数据失败: ${e.message}"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    fun clearClearDataSuccess() {
        _uiState.value = _uiState.value.copy(showClearDataSuccess = false)
    }
}

data class SettingsUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val showClearDataSuccess: Boolean = false
)
