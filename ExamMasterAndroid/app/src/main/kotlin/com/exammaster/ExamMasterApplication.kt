package com.exammaster

import android.app.Application
import android.content.ComponentName
import android.content.pm.PackageManager
import android.widget.Toast
import com.exammaster.data.models.AppIcon
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@HiltAndroidApp
class ExamMasterApplication : Application() {
    
    // 用于在应用程序级别执行协程
    private val appScope = CoroutineScope(Dispatchers.Main)
    
    companion object {
        private lateinit var instance: ExamMasterApplication
        
        fun getInstance(): ExamMasterApplication {
            return instance
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
    }
      // 更改应用图标
    fun changeAppIcon(appIcon: AppIcon): Boolean {
        return try {
            val packageManager = packageManager

            // 停用所有图标别名
            disableAllIconAliases(packageManager)

            // 启用选定的图标
            val componentName = getComponentNameForIcon(appIcon)
            packageManager.setComponentEnabledSetting(
                componentName,
                PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                PackageManager.DONT_KILL_APP
            )

            // 显示 Toast 消息
            Toast.makeText(applicationContext, "图标已更改，重启应用后生效", Toast.LENGTH_SHORT).show()
            true
        } catch (e: Exception) {
            // 显示错误 Toast 消息
            Toast.makeText(applicationContext, "图标更改失败", Toast.LENGTH_SHORT).show()
            e.printStackTrace()
            false
        }
    }
      // 停用所有图标别名
    private fun disableAllIconAliases(packageManager: PackageManager) {
        try {
            val aliases = listOf(
                "$packageName.MainActivity.Default",
                "$packageName.MainActivity.Blue",
                "$packageName.MainActivity.Green",
                "$packageName.MainActivity.Red",
                "$packageName.MainActivity.Orange",
                "$packageName.MainActivity.Teal"
            )

            aliases.forEach { alias ->
                packageManager.setComponentEnabledSetting(
                    ComponentName(this, alias),
                    PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    PackageManager.DONT_KILL_APP
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    // 获取对应图标的组件名
    private fun getComponentNameForIcon(appIcon: AppIcon): ComponentName {
        return when (appIcon) {
            AppIcon.DEFAULT -> ComponentName(this, MainActivity::class.java)
            AppIcon.BLUE -> ComponentName(this, "$packageName.MainActivity.Blue")
            AppIcon.GREEN -> ComponentName(this, "$packageName.MainActivity.Green")
            AppIcon.RED -> ComponentName(this, "$packageName.MainActivity.Red")
            AppIcon.ORANGE -> ComponentName(this, "$packageName.MainActivity.Orange")
            AppIcon.TEAL -> ComponentName(this, "$packageName.MainActivity.Teal")
        }
    }
}