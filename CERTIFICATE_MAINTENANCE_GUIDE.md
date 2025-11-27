# 证书维护指南

本文档说明如何获取和管理 Android 和 iOS 应用的证书信息，以及如何确保敏感信息不被上传到 GitHub。

## 目录

- [Android 证书信息](#android-证书信息)
- [iOS 证书信息](#ios-证书信息)
- [安全配置](#安全配置)
- [常见问题](#常见问题)

---

## Android 证书信息

### 证书文件位置

```
flutter_app/android/app/exam-master-release.jks
```

### 获取证书指纹

#### 1. 获取完整证书信息

```bash
cd flutter_app/android/app
keytool -list -v -keystore exam-master-release.jks -alias exam-master-key
```

输入密钥库密码后，将显示：
- SHA1 指纹
- SHA256 指纹
- 证书所有者信息
- 证书有效期

#### 2. 获取 MD5 指纹

```bash
keytool -exportcert -alias exam-master-key \
  -keystore exam-master-release.jks \
  -storepass <密钥库密码> | openssl dgst -md5
```

输出示例：
```
MD5(stdin)= b63188ec2b0ef62859e9680f94b2f949
```

格式化后（用于某些平台）：
```
B6:31:88:EC:2B:0E:F6:28:59:E9:68:0F:94:B2:F9:49
```

#### 3. 导出公钥证书

导出为 PEM 格式：
```bash
keytool -exportcert -alias exam-master-key \
  -keystore exam-master-release.jks \
  -storepass <密钥库密码> \
  -rfc -file android-cert.pem
```

查看公钥详细信息：
```bash
keytool -exportcert -alias exam-master-key \
  -keystore exam-master-release.jks \
  -storepass <密钥库密码> | \
  openssl x509 -inform DER -text -noout
```

### Android 应用信息

- **包名**: `com.exammaster.exam_master_app`
- **密钥别名**: `exam-master-key`
- **证书有效期**: 2025年11月6日 - 2053年3月24日

### 第三方平台配置

在配置以下平台时需要使用证书指纹：

#### 高德地图 / 百度地图
- **PackageName**: `com.exammaster.exam_master_app`
- **SHA1 指纹**: 从上述命令获取（大写，带冒号）

#### 微信开放平台
- **应用包名**: `com.exammaster.exam_master_app`
- **应用签名**: SHA1 指纹（小写，无冒号）

#### Firebase / Google Play
- **包名**: `com.exammaster.exam_master_app`
- **SHA1 指纹**: 从上述命令获取
- **SHA256 指纹**: 从上述命令获取

---

## iOS 证书信息

### Bundle ID

```
com.exammaster.examMasterApp
```

### 从 mobileprovision 文件获取证书信息

#### 1. 查找 mobileprovision 文件

构建后的位置：
```
flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision
```

或者从 Xcode 导出：
```
~/Library/MobileDevice/Provisioning Profiles/
```

#### 2. 读取 mobileprovision 内容

```bash
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision
```

#### 3. 提取证书 SHA-1 指纹

```bash
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision | \
  plutil -extract DeveloperCertificates.0 raw -o - - | \
  base64 -D | \
  openssl x509 -inform DER -fingerprint -sha1 -noout
```

输出示例：
```
sha1 Fingerprint=6F:5E:AC:48:0A:FD:1D:44:61:E2:1C:0F:AB:AC:29:CD:15:2C:57:5F
```

#### 4. 提取公钥（PEM 格式）

```bash
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision | \
  plutil -extract DeveloperCertificates.0 raw -o - - | \
  base64 -D | \
  openssl x509 -inform DER -pubkey -noout
```

#### 5. 提取公钥（Base64 格式）

```bash
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision | \
  plutil -extract DeveloperCertificates.0 raw -o - - | \
  base64 -D | \
  openssl x509 -inform DER -pubkey -noout | \
  openssl rsa -pubin -outform DER 2>/dev/null | \
  base64
```

#### 6. 查看证书详细信息

```bash
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision | \
  plutil -extract DeveloperCertificates.0 raw -o - - | \
  base64 -D | \
  openssl x509 -inform DER -text -noout
```

### 从钥匙串访问获取证书

#### 方法 1: 使用 Keychain Access 应用

1. 打开"钥匙串访问"（Keychain Access）
2. 在左侧选择"登录" > "我的证书"
3. 找到 "Apple Development: xinyu-c@outlook.com" 证书
4. 右键点击 > "显示简介"
5. 在"指纹"部分可以看到 SHA-1 值

#### 方法 2: 使用命令行

列出所有开发证书：
```bash
security find-identity -v -p codesigning
```

导出特定证书：
```bash
security find-certificate -c "Apple Development" -p > ios-dev-cert.pem
```

查看证书指纹：
```bash
security find-certificate -c "Apple Development" -p | \
  openssl x509 -fingerprint -sha1 -noout
```

### iOS 应用信息

- **Bundle ID**: `com.exammaster.examMasterApp`
- **Team ID**: `TY9QCK8ALL`
- **Team Name**: Shayne Chen
- **证书类型**: Apple Development
- **证书有效期**: 2025年9月4日 - 2026年9月4日

---

## 安全配置

### .gitignore 配置

确保以下文件**绝不**被提交到 Git：

```gitignore
# Android 签名文件（私密信息 - 绝不提交！）
*.jks
*.keystore
android/app/key.properties
flutter_app/android/app/*.jks
flutter_app/android/app/*.keystore
flutter_app/android/app/key.properties

# iOS 签名文件（私密信息 - 绝不提交！）
*.p12
*.cer
*.certSigningRequest
*.mobileprovision
!flutter_app/build/ios/*/Runner.app/embedded.mobileprovision

# 包含敏感信息的文档
ANDROID_SIGNING_INFO.md
IOS_SIGNING_INFO.md
SIGNING_SUMMARY_PRIVATE.txt
*_PRIVATE.txt
*_PRIVATE.md
generate_*_signing.sh

# Xcode 用户特定文件
*.xcuserstate
*.xcuserdatad/
xcuserdata/

# 证书导出文件
*-cert.pem
*-key.pem
*.pem
```

### 验证 .gitignore 是否生效

检查哪些文件会被 Git 跟踪：
```bash
git status --ignored
```

检查特定文件是否被忽略：
```bash
git check-ignore -v flutter_app/android/app/exam-master-release.jks
```

如果文件已经被提交，需要从 Git 历史中移除：
```bash
# 仅从 Git 移除，保留本地文件
git rm --cached flutter_app/android/app/exam-master-release.jks

# 提交更改
git commit -m "Remove sensitive keystore file from Git"
```

### 密钥库备份策略

**重要：** 密钥库文件丢失将导致无法更新已发布的应用！

建议备份位置（至少选择 2-3 个）：

1. **加密云盘**
   - Google Drive（使用加密文件夹）
   - iCloud（使用加密磁盘映像）
   - Dropbox（使用加密容器）

2. **物理存储**
   - 加密 U 盘
   - 加密移动硬盘
   - 放在保险箱中

3. **密码管理器**
   - 1Password（安全附件功能）
   - LastPass
   - Bitwarden

4. **团队共享**
   - 公司加密文件服务器
   - 团队密码管理器的安全库

### 密码管理

**密钥库密码**应该：
- ✅ 使用强密码（至少 16 位，包含大小写字母、数字、特殊字符）
- ✅ 存储在密码管理器中
- ✅ 与团队核心成员共享（通过安全渠道）
- ❌ 不要写在代码或文档中
- ❌ 不要通过普通聊天工具发送
- ❌ 不要使用简单密码

**创建密码管理器条目**（推荐格式）：
```
标题: EXAM-MASTER Android Release Keystore
用户名: exam-master-key
密码: [实际的密钥库密码]
网址: -
备注:
  密钥库路径: flutter_app/android/app/exam-master-release.jks
  密钥别名: exam-master-key
  包名: com.exammaster.exam_master_app
  SHA1: 6A:92:BD:0D:65:85:68:E0:5B:FA:B6:BF:61:59:9B:63:73:98:D9:F0
  创建日期: 2025-11-06
  有效期至: 2053-03-24
附件: exam-master-release.jks (备份)
```

---

## 常见问题

### Q: 证书指纹会变化吗？

**不会！** 只要使用同一个密钥库文件，证书指纹就永远不变。修改代码、重新打包都不会影响证书指纹。

### Q: 什么情况下需要证书指纹？

配置第三方 SDK 或服务时，例如：
- 地图 SDK（高德、百度、Google Maps）
- 社交登录（微信、QQ、微博）
- 推送服务（Firebase、极光推送）
- 支付 SDK（支付宝、微信支付）
- 应用商店（Google Play Console）

### Q: 如何区分 Debug 和 Release 证书？

**Debug 证书**：
- 自动生成，位于 `~/.android/debug.keystore`
- 只用于开发测试
- 不能用于发布应用

**Release 证书**：
- 手动生成，自己保管
- 用于发布到应用商店
- 必须妥善备份

获取 debug 证书指纹：
```bash
keytool -list -v -keystore ~/.android/debug.keystore \
  -alias androiddebugkey -storepass android -keypass android
```

### Q: 如何验证 APK 使用的证书？

```bash
# 查看 APK 签名
keytool -printcert -jarfile app-release.apk

# 对比密钥库证书
keytool -list -v -keystore exam-master-release.jks -alias exam-master-key

# 两者的 SHA1/SHA256 应该完全一致
```

### Q: iOS 证书过期了怎么办？

Apple Development 证书每年过期一次，过期后需要：

1. 在 Apple Developer 网站更新证书
2. 下载新的 mobileprovision 文件
3. 在 Xcode 中更新配置
4. 重新构建应用

**注意**：更新证书**不会**影响已发布的应用，用户不需要重新下载。

### Q: 多人协作如何管理证书？

**推荐方案**：

1. **发布负责人**持有 Release 证书
2. **开发人员**使用各自的 Debug 证书
3. 使用 **CI/CD** 自动化构建发布版本
4. 证书存储在 **CI/CD 环境变量**中（加密）
5. 文档记录证书指纹供团队配置第三方服务

**不推荐**：
- ❌ 共享密钥库文件通过聊天工具
- ❌ 提交密钥库到 Git
- ❌ 所有人使用同一个开发证书

### Q: 误删了密钥库文件怎么办？

**情况 1：应用尚未发布**
- 可以生成新的密钥库
- 更新第三方平台的证书指纹

**情况 2：应用已发布**
- 从备份恢复（这就是为什么备份至关重要！）
- 如果没有备份：
  - Android：无法更新应用，需要更换包名重新上架
  - iOS：联系 Apple 支持，可能可以重新颁发

### Q: 如何检查密钥库是否损坏？

```bash
# 尝试列出密钥库内容
keytool -list -keystore exam-master-release.jks

# 如果出错，密钥库可能已损坏，需要使用备份
```

---

## 快速参考命令

### Android

```bash
# 查看证书完整信息
keytool -list -v -keystore exam-master-release.jks

# 获取 SHA1（带冒号）
keytool -list -v -keystore exam-master-release.jks | grep SHA1

# 获取 SHA1（无冒号，小写 - 用于微信）
keytool -list -v -keystore exam-master-release.jks | grep SHA1 | \
  awk '{print $2}' | tr -d ':' | tr '[:upper:]' '[:lower:]'

# 获取 MD5
keytool -exportcert -alias exam-master-key \
  -keystore exam-master-release.jks | openssl dgst -md5

# 验证 APK 签名
keytool -printcert -jarfile app-release.apk
```

### iOS

```bash
# 从构建产物提取证书 SHA1
security cms -D -i flutter_app/build/ios/iphoneos/Runner.app/embedded.mobileprovision | \
  plutil -extract DeveloperCertificates.0 raw -o - - | \
  base64 -D | openssl x509 -inform DER -fingerprint -sha1 -noout

# 列出钥匙串中的签名证书
security find-identity -v -p codesigning

# 查看证书详细信息
security find-certificate -c "Apple Development" -p | openssl x509 -text -noout
```

---

## 维护清单

### 每次发布前

- [ ] 确认使用正确的 Release 证书
- [ ] 验证 APK/IPA 签名正确
- [ ] 检查证书有效期
- [ ] 测试应用安装和更新

### 每季度

- [ ] 验证密钥库备份可用性
- [ ] 检查证书过期时间
- [ ] 审查 .gitignore 配置
- [ ] 更新文档中的证书信息

### 证书更新时（iOS）

- [ ] 下载新的证书和 mobileprovision
- [ ] 更新 Xcode 配置
- [ ] 重新构建并测试
- [ ] 记录新的证书指纹
- [ ] 通知团队成员

### 新成员加入

- [ ] 提供本维护指南
- [ ] 说明证书管理流程
- [ ] 分享必要的证书指纹（不是密钥库！）
- [ ] 配置其 Debug 开发环境

---

## 联系与支持

遇到证书相关问题：

1. 查看本文档的常见问题部分
2. 查阅官方文档：
   - [Flutter 官方部署指南](https://docs.flutter.dev/deployment)
   - [Android 应用签名](https://developer.android.com/studio/publish/app-signing)
   - [Apple 开发者文档](https://developer.apple.com/documentation/)
3. 联系项目维护者

---

**最后更新**: 2025-11-06

**重要提醒**:
- 🔒 **绝不**将密钥库文件提交到 Git
- 💾 **务必**备份密钥库到多个安全位置
- 🔑 **密钥库密码**使用密码管理器保存
- 📋 **证书指纹**可以公开，但**密钥库文件和密码**必须保密
