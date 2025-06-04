package com.exammaster.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.hilt.navigation.compose.hiltViewModel
import com.exammaster.data.models.ThemeMode
import com.exammaster.ui.viewmodel.SettingsViewModel

@Composable
fun ExamMasterTheme(
    settingsViewModel: SettingsViewModel = hiltViewModel(),
    content: @Composable () -> Unit
) {
    val settings by settingsViewModel.settings.collectAsState()
    
    val darkTheme = when (settings.themeMode) {
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }
    
    val colorScheme = if (darkTheme) {
        darkColorScheme()
    } else {
        lightColorScheme()
    }
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}
