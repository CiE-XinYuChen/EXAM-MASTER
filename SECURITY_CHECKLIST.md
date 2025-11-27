# 安全检查清单

## 🔒 在提交代码前，请确认：

### ✅ 必须检查的项目

- [ ] 没有提交 `.jks` 或 `.keystore` 文件
- [ ] 没有提交 `.p12`、`.cer` 或 `.mobileprovision` 文件
- [ ] 没有提交 `key.properties` 文件
- [ ] 没有提交包含密码的文档（`*_PRIVATE.*`）
- [ ] 没有在代码中硬编码密码或密钥

### 📋 快速验证命令

```bash
# 检查是否有敏感文件将被提交
git status | grep -E "(jks|keystore|p12|cer|_PRIVATE)"

# 验证 .gitignore 是否生效
git check-ignore -v flutter_app/android/app/exam-master-release.jks
git check-ignore -v SIGNING_SUMMARY_PRIVATE.txt

# 查看即将提交的文件
git status --short
```

### 🆘 如果不小心提交了敏感文件

```bash
# 1. 从 Git 移除（保留本地文件）
git rm --cached <敏感文件路径>

# 2. 提交移除操作
git commit -m "Remove sensitive file from Git"

# 3. 如果已经推送到远程，需要强制推送（谨慎使用）
# git push --force

# 4. 更换密钥库并重新生成证书（推荐）
```

## 📚 完整指南

详细的证书管理和安全配置请参考：
- [证书维护指南](CERTIFICATE_MAINTENANCE_GUIDE.md)
- [Android 签名指南](ANDROID_SIGNING_GUIDE.md)

## 🔑 密钥库文件位置（本地）

**这些文件绝不应该出现在 Git 中！**

### Android
```
flutter_app/android/app/exam-master-release.jks
flutter_app/android/app/key.properties
```

### iOS
```
*.p12
*.cer
*.mobileprovision (build 目录除外)
```

## 📞 需要帮助？

如果对安全配置有疑问，请：
1. 查看 [证书维护指南](CERTIFICATE_MAINTENANCE_GUIDE.md)
2. 联系项目维护者
3. **不要**在不确定的情况下提交代码

---

**记住**: 证书指纹可以公开，但密钥库文件和密码必须保密！
