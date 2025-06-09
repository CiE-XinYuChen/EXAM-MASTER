package com.exammaster.data.models

/**
 * 主题模式枚举
 */
enum class ThemeMode {
    LIGHT,      // 浅色主题
    DARK,       // 深色主题
    SYSTEM      // 跟随系统
}

/**
 * 主题颜色枚举
 */
enum class ThemeColor {
    DEFAULT,    // 默认紫色
    BLUE,       // 蓝色
    GREEN,      // 绿色
    RED,        // 红色
    ORANGE,     // 橙色
    TEAL        // 青色
}

/**
 * 应用图标枚举
 */
enum class AppIcon {
    DEFAULT,    // 默认紫色图标
    BLUE,       // 蓝色图标
    GREEN,      // 绿色图标
    RED,        // 红色图标
    ORANGE,     // 橙色图标
    TEAL        // 青色图标
}

/**
 * 设置数据模型
 */
data class Settings(
    val themeMode: ThemeMode = ThemeMode.SYSTEM,
    val themeColor: ThemeColor = ThemeColor.DEFAULT,
    val appIcon: AppIcon = AppIcon.DEFAULT,
    val notificationsEnabled: Boolean = true,
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val autoSubmitTimed: Boolean = true,
    val defaultQuestionCount: Int = 20,
    val showCorrectAnswer: Boolean = true,
    val enableProgressTracking: Boolean = true,
    val autoSaveProgress: Boolean = true,
    val enableStatistics: Boolean = true,
    val reminderInterval: Int = 24, // 小时
    val autoNextOnCorrect: Boolean = true
)
