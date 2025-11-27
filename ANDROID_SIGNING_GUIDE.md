# Android 应用签名配置指南

## 📱 关于应用签名

Android 应用必须使用数字签名才能安装到设备上。签名用于：
- ✅ 验证应用来源和开发者身份
- ✅ 防止应用被篡改
- ✅ 确保应用更新的连续性

## ❓ 常见问题

### 签名会变化吗？

**不会！** 签名**不会因为修改代码而变化**。

- 签名基于密钥库文件
- 只要使用同一个密钥库，签名指纹就不变
- 修改代码后重新打包，签名仍然相同

### 为什么要保护密钥库？

⚠️ **密钥库丢失的严重后果**：
- ❌ 无法更新已发布的应用
- ❌ 需要更换包名重新上架
- ❌ 用户需要卸载旧版本才能安装新版本
- ❌ 所有评分和下载记录清零

---

## 🔑 生成签名密钥

### 1. 创建密钥库文件

```bash
keytool -genkey -v \
  -keystore your-app-release.jks \
  -alias your-key-alias \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

按提示输入：
- 密钥库密码（需要记住！）
- 密钥密码（需要记住！）
- 姓名、组织等信息

### 2. 查看密钥信息

```bash
keytool -list -v -keystore your-app-release.jks -alias your-key-alias
```

会显示：
- SHA1 指纹（用于第三方平台配置）
- SHA256 指纹（用于 Firebase 等）
- 证书有效期等信息

---

## 🛠️ 配置 Flutter 项目

### 1. 存放密钥库文件

将 `.jks` 文件放到：
```
flutter_app/android/app/your-app-release.jks
```

### 2. 创建 key.properties

在 `flutter_app/android/app/key.properties`:

```properties
storePassword=你的密钥库密码
keyPassword=你的密钥密码
keyAlias=你的密钥别名
storeFile=your-app-release.jks
```

### 3. 修改 build.gradle.kts

在 `flutter_app/android/app/build.gradle.kts`:

```kotlin
// 在 android { } 块之前添加
val keystorePropertiesFile = rootProject.file("app/key.properties")
val keystoreProperties = java.util.Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(java.io.FileInputStream(keystorePropertiesFile))
}

android {
    namespace = "com.exammaster.exam_master_app"  // 你的包名
    // ... 其他配置 ...

    // 添加签名配置
    signingConfigs {
        create("release") {
            if (keystorePropertiesFile.exists()) {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            // 启用代码混淆（可选但推荐）
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### 4. 更新 .gitignore

⚠️ **重要**：确保以下文件不被提交到 Git！

在 `.gitignore` 中添加：

```gitignore
# Android 签名文件（私密信息 - 绝不提交！）
*.jks
*.keystore
android/app/key.properties

# 签名信息文档（如果包含真实密码和指纹）
ANDROID_SIGNING_INFO.md
```

---

## 🚀 构建发布版本

### 构建 APK
```bash
cd flutter_app
flutter build apk --release
```

输出位置: `build/app/outputs/flutter-apk/app-release.apk`

### 构建 App Bundle（推荐用于 Google Play）
```bash
flutter build appbundle --release
```

输出位置: `build/app/outputs/bundle/release/app-release.aab`

---

## ✅ 验证签名

### 查看 APK 的签名信息
```bash
keytool -printcert -jarfile app-release.apk
```

### 确认签名是否正确
```bash
# 查看 APK 的 SHA1
keytool -printcert -jarfile app-release.apk | grep SHA1

# 对比密钥库的 SHA1
keytool -list -v -keystore your-app-release.jks -alias your-key-alias | grep SHA1
```

两者应该完全一致！

---

## 📋 第三方平台配置

配置第三方服务时需要提供：

### Google Play Console
- **包名**: `com.exammaster.exam_master_app`
- **SHA1 指纹**: 从密钥库中获取

### Firebase
- **包名**: `com.exammaster.exam_master_app`
- **SHA1 指纹**: 从密钥库中获取
- **SHA256 指纹**: 从密钥库中获取

### 微信开放平台
- **应用包名**: `com.exammaster.exam_master_app`
- **应用签名**: SHA1 指纹（小写且无冒号）

### 高德地图/百度地图
- **PackageName**: `com.exammaster.exam_master_app`
- **SHA1**: 从密钥库中获取

---

## 🔒 安全最佳实践

### 1. 密钥库管理

✅ **要做的**:
- 备份密钥库文件到安全的地方（至少 3 份）
- 使用强密码保护密钥库
- 记录密钥库信息（密码、别名等）在安全的密码管理器中
- 定期验证备份可用性

❌ **不要做的**:
- 不要提交密钥库到版本控制系统
- 不要在公开的文档中写密钥库密码
- 不要分享密钥库给他人
- 不要在不安全的地方存储密钥库

### 2. 团队协作

如果多人开发：
- 只有发布负责人持有密钥库
- 其他开发者使用 debug 签名调试
- 通过 CI/CD 自动构建发布版本
- 密钥库存储在安全的 CI/CD 环境变量中

### 3. 备份策略

建议存储位置（选择 2-3 个）：
- ✅ 公司/团队的加密文件服务器
- ✅ 个人加密云盘（Google Drive、iCloud 等）
- ✅ 加密 U 盘/移动硬盘
- ✅ 密码管理器的安全附件

---

## 📝 快速参考

### 包名
```
com.exammaster.exam_master_app
```

### 获取签名指纹

```bash
# 查看完整信息
keytool -list -v -keystore your-app-release.jks

# 只看 SHA1
keytool -list -v -keystore your-app-release.jks | grep SHA1

# 只看 SHA256
keytool -list -v -keystore your-app-release.jks | grep SHA256
```

### 常用命令

```bash
# 构建发布 APK
flutter build apk --release

# 构建 App Bundle
flutter build appbundle --release

# 验证 APK 签名
keytool -printcert -jarfile app-release.apk

# 安装发布版到设备
flutter install --release
```

---

## 🆘 问题排查

### Q: 提示"密钥库已损坏"
A: 密钥库文件可能损坏，使用备份替换

### Q: 提示"密码错误"
A: 检查 key.properties 中的密码是否正确

### Q: 无法安装 APK
A: 检查签名是否正确，是否使用了正确的密钥库

### Q: 应用商店提示签名不匹配
A: 更新时必须使用首次发布的同一密钥库

---

## 📞 帮助与支持

遇到问题？
- 查看 [Flutter 官方文档](https://docs.flutter.dev/deployment/android)
- 访问 [项目 Issues](https://github.com/CiE-XinYuChen/EXAM-MASTER/issues)
- 联系项目维护者

---

**提醒**: 本指南不包含真实的密钥库和密码信息。每个开发者应该生成自己的签名密钥。

**⚠️ 请务必妥善保管您的密钥库文件！**
