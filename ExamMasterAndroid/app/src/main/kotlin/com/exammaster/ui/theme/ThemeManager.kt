package com.exammaster.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.graphics.toArgb
import android.app.Activity
import androidx.core.view.WindowCompat
import androidx.hilt.navigation.compose.hiltViewModel
import com.exammaster.data.models.ThemeColor
import com.exammaster.data.models.ThemeMode
import com.exammaster.ui.viewmodel.SettingsViewModel

/**
 * 获取指定主题颜色和亮暗模式的颜色方案
 */
@Composable
fun getThemeColorScheme(themeColor: ThemeColor, isDarkTheme: Boolean) = when (themeColor) {
    ThemeColor.DEFAULT -> if (isDarkTheme) DefaultDarkColorScheme else DefaultLightColorScheme
    ThemeColor.BLUE -> if (isDarkTheme) BlueDarkColorScheme else BlueLightColorScheme
    ThemeColor.GREEN -> if (isDarkTheme) GreenDarkColorScheme else GreenLightColorScheme
    ThemeColor.RED -> if (isDarkTheme) RedDarkColorScheme else RedLightColorScheme
    ThemeColor.ORANGE -> if (isDarkTheme) OrangeDarkColorScheme else OrangeLightColorScheme
    ThemeColor.TEAL -> if (isDarkTheme) TealDarkColorScheme else TealLightColorScheme
}

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
    
    // 根据选择的主题颜色和亮暗模式获取颜色方案
    val colorScheme = getThemeColorScheme(settings.themeColor, darkTheme)
    
    // 更新状态栏颜色
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}
