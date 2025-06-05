# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# 保留行号信息，方便调试
-keepattributes SourceFile,LineNumberTable

# 保留注解
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes Exceptions

# 保留R资源类
-keep class **.R
-keep class **.R$* {
    <fields>;
}

# 保留应用程序类
-keep class com.exammaster.ExamMasterApplication { *; }
-keep class com.exammaster.MainActivity { *; }

# 保留所有Model类
-keep class com.exammaster.data.models.** { *; }

# 保留所有Entity类
-keep class com.exammaster.data.database.entities.** { *; }

# 保留所有DAO类
-keep class com.exammaster.data.database.dao.** { *; }

# 保留所有Repository类
-keep class com.exammaster.data.repository.** { *; }

# 保留所有ViewModel类
-keep class com.exammaster.ui.viewmodel.** { *; }

# 保留所有依赖注入模块
-keep class com.exammaster.di.** { *; }

# 保留数据加载器
-keep class com.exammaster.data.QuestionDataLoader { *; }

# 保留DataStore相关类
-keep class com.exammaster.data.datastore.** { *; }

# 保留Compose相关类
-keep class androidx.compose.** { *; }
-keepclassmembers class androidx.compose.** { *; }

# 保留Kotlin协程相关类
-keep class kotlinx.coroutines.** { *; }
-keepclassmembers class kotlinx.coroutines.** { *; }

# Room数据库相关
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-keep @androidx.room.Dao class *
-dontwarn androidx.room.paging.**

# Hilt相关
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ApplicationComponentManager { *; }
-keep @dagger.hilt.android.lifecycle.HiltViewModel class *

# 序列化相关
-keep class kotlinx.serialization.** { *; }
-keep class * implements kotlinx.serialization.KSerializer { *; }

# Gson相关
-keep class com.google.gson.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
-dontwarn sun.misc.**
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Navigation相关
-keep class androidx.navigation.** { *; }
-keepnames class androidx.navigation.fragment.NavHostFragment

# 保留枚举类
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# 保留Parcelable实现类
-keep class * implements android.os.Parcelable {
  public static final android.os.Parcelable$Creator *;
}

# 保留Serializable实现类
-keep class * implements java.io.Serializable { *; }

# 保留native方法
-keepclasseswithmembernames class * {
    native <methods>;
}

# 保留自定义View
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
    public void set*(...);
    *** get*();
}