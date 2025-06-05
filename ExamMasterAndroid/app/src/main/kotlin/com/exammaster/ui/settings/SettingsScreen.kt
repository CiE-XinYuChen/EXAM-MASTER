package com.exammaster.ui.settings

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.DarkMode
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.exammaster.data.models.AppIcon
import com.exammaster.data.models.ThemeMode
import com.exammaster.data.models.ThemeColor
import com.exammaster.ui.settings.components.*
import com.exammaster.ui.viewmodel.SettingsViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    navController: NavController,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val settings by viewModel.settings.collectAsState()
    val uiState by viewModel.uiState.collectAsState()
    var showClearDataDialog by remember { mutableStateOf(false) }

    // 显示错误信息
    val context = LocalContext.current
    LaunchedEffect(uiState.errorMessage) {
        uiState.errorMessage?.let {
            Toast.makeText(context, it, Toast.LENGTH_LONG).show()
            viewModel.clearError()
        }
    }

    // 显示清除数据成功提示
    LaunchedEffect(uiState.showClearDataSuccess) {
        if (uiState.showClearDataSuccess) {
            viewModel.clearClearDataSuccess()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("设置") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
        ) {
            // 外观设置
            SettingSectionTitle("外观设置")
            
            SelectionSettingItem(
                title = "主题模式",
                subtitle = when (settings.themeMode) {
                    ThemeMode.LIGHT -> "浅色"
                    ThemeMode.DARK -> "深色"
                    ThemeMode.SYSTEM -> "跟随系统"
                },
                icon = Icons.Outlined.DarkMode,
                selectedValue = settings.themeMode.name,
                options = listOf(
                    ThemeMode.LIGHT.name to "浅色",
                    ThemeMode.DARK.name to "深色",
                    ThemeMode.SYSTEM.name to "跟随系统"
                ),
                onSelectionChange = { mode ->
                    viewModel.updateThemeMode(ThemeMode.valueOf(mode))
                }
            )
            
            SelectionSettingItem(
                title = "主题颜色",
                subtitle = when (settings.themeColor) {
                    ThemeColor.DEFAULT -> "默认紫色"
                    ThemeColor.BLUE -> "蓝色"
                    ThemeColor.GREEN -> "绿色"
                    ThemeColor.RED -> "红色"
                    ThemeColor.ORANGE -> "橙色"
                    ThemeColor.TEAL -> "青色"
                },
                icon = Icons.Default.Palette,
                selectedValue = settings.themeColor.name,
                options = listOf(
                    ThemeColor.DEFAULT.name to "默认紫色",
                    ThemeColor.BLUE.name to "蓝色",
                    ThemeColor.GREEN.name to "绿色",
                    ThemeColor.RED.name to "红色",
                    ThemeColor.ORANGE.name to "橙色",
                    ThemeColor.TEAL.name to "青色"
                ),
                onSelectionChange = { color ->
                    viewModel.updateThemeColor(ThemeColor.valueOf(color))
                }
            )
            
            SelectionSettingItem(
                title = "应用图标",
                subtitle = when (settings.appIcon) {
                    AppIcon.DEFAULT -> "默认紫色"
                    AppIcon.BLUE -> "蓝色"
                    AppIcon.GREEN -> "绿色"
                    AppIcon.RED -> "红色"
                    AppIcon.ORANGE -> "橙色"
                    AppIcon.TEAL -> "青色"
                },
                icon = Icons.Default.AppShortcut,
                selectedValue = settings.appIcon.name,
                options = listOf(
                    AppIcon.DEFAULT.name to "默认紫色",
                    AppIcon.BLUE.name to "蓝色",
                    AppIcon.GREEN.name to "绿色",
                    AppIcon.RED.name to "红色",
                    AppIcon.ORANGE.name to "橙色",
                    AppIcon.TEAL.name to "青色"
                ),
                onSelectionChange = { icon ->
                    // 只更新应用图标，Toast会在ViewModel中显示
                    viewModel.updateAppIcon(AppIcon.valueOf(icon))
                }
            )

            SettingDivider()

            // 通知设置
            SettingSectionTitle("通知设置")
            
            SwitchSettingItem(
                title = "启用通知",
                subtitle = "接收学习提醒和重要通知",
                icon = Icons.Default.Notifications,
                checked = settings.notificationsEnabled,
                onCheckedChange = viewModel::updateNotificationsEnabled
            )

            SwitchSettingItem(
                title = "启用声音",
                subtitle = "播放通知声音",
                icon = Icons.Default.VolumeUp,
                checked = settings.soundEnabled,
                onCheckedChange = viewModel::updateSoundEnabled
            )

            SwitchSettingItem(
                title = "启用震动",
                subtitle = "通知时震动提醒",
                icon = Icons.Default.Vibration,
                checked = settings.vibrationEnabled,
                onCheckedChange = viewModel::updateVibrationEnabled
            )

            NumberInputSettingItem(
                title = "提醒间隔",
                subtitle = "${settings.reminderInterval} 小时",
                icon = Icons.Default.Schedule,
                value = settings.reminderInterval,
                range = 1..72,
                onValueChange = viewModel::updateReminderInterval
            )

            SettingDivider()

            // 答题设置
            SettingSectionTitle("答题设置")
            
            SwitchSettingItem(
                title = "限时模式自动提交",
                subtitle = "时间到后自动提交答案",
                icon = Icons.Default.Timer,
                checked = settings.autoSubmitTimed,
                onCheckedChange = viewModel::updateAutoSubmitTimed
            )

            NumberInputSettingItem(
                title = "默认题目数量",
                subtitle = "${settings.defaultQuestionCount} 道题",
                icon = Icons.Default.Quiz,
                value = settings.defaultQuestionCount,
                range = 5..100,
                onValueChange = viewModel::updateDefaultQuestionCount
            )

            SwitchSettingItem(
                title = "显示正确答案",
                subtitle = "答题后显示正确答案解析",
                icon = Icons.Default.Lightbulb,
                checked = settings.showCorrectAnswer,
                onCheckedChange = viewModel::updateShowCorrectAnswer
            )

            SwitchSettingItem(
                title = "回答正确自动下一题",
                subtitle = "答对后自动跳转到下一题",
                icon = Icons.Default.ArrowForward,
                checked = settings.autoNextOnCorrect,
                onCheckedChange = viewModel::updateAutoNextOnCorrect
            )

            SettingDivider()

            // 数据设置
            SettingSectionTitle("数据设置")
            
            SwitchSettingItem(
                title = "启用进度跟踪",
                subtitle = "记录学习进度和答题历史",
                icon = Icons.Default.TrendingUp,
                checked = settings.enableProgressTracking,
                onCheckedChange = viewModel::updateEnableProgressTracking
            )

            SwitchSettingItem(
                title = "自动保存进度",
                subtitle = "自动保存答题进度",
                icon = Icons.Default.Save,
                checked = settings.autoSaveProgress,
                onCheckedChange = viewModel::updateAutoSaveProgress
            )

            SwitchSettingItem(
                title = "启用统计功能",
                subtitle = "收集学习统计数据",
                icon = Icons.Default.Analytics,
                checked = settings.enableStatistics,
                onCheckedChange = viewModel::updateEnableStatistics
            )

            SettingItem(
                title = "清除所有数据",
                subtitle = "删除所有答题记录、收藏和设置",
                icon = Icons.Default.DeleteForever,
                onClick = { showClearDataDialog = true }
            )

            Spacer(modifier = Modifier.height(16.dp))
        }
    }

    // 清除数据确认对话框
    if (showClearDataDialog) {
        AlertDialog(
            onDismissRequest = { showClearDataDialog = false },
            title = { Text("清除所有数据") },
            text = { 
                Text(
                    "此操作将删除所有答题记录、收藏题目、学习统计和个人设置。\n\n此操作不可撤销，确定要继续吗？"
                ) 
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.clearAllData()
                        showClearDataDialog = false
                    }
                ) {
                    Text("确定删除", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDataDialog = false }) {
                    Text("取消")
                }
            }
        )
    }

    // 加载指示器
    if (uiState.isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = androidx.compose.ui.Alignment.Center
        ) {
            CircularProgressIndicator()
        }
    }
}
