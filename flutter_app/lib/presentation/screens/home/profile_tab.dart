import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

/// Profile Tab
/// 个人中心标签
class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  Future<void> _handleLogout(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认退出'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      await context.read<AuthProvider>().logout();
      if (context.mounted) {
        Navigator.of(context).pushReplacementNamed('/login');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          final user = authProvider.currentUser;

          return ListView(
            children: [
              // User Header
              Container(
                padding: const EdgeInsets.all(24),
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 40,
                      backgroundColor: Theme.of(context).primaryColor,
                      child: Text(
                        user?.username.substring(0, 1).toUpperCase() ?? 'U',
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            user?.username ?? '未登录',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            user?.email ?? '',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Menu Items
              ListTile(
                leading: const Icon(Icons.person_outline),
                title: const Text('个人信息'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to profile edit
                },
              ),
              ListTile(
                leading: const Icon(Icons.card_membership_outlined),
                title: const Text('我的权限'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to my access
                },
              ),
              ListTile(
                leading: const Icon(Icons.favorite_outline),
                title: const Text('我的收藏'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to favorites
                },
              ),
              ListTile(
                leading: const Icon(Icons.error_outline),
                title: const Text('错题本'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to wrong questions
                },
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.settings_outlined),
                title: const Text('设置'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to settings
                },
              ),
              ListTile(
                leading: const Icon(Icons.help_outline),
                title: const Text('帮助与反馈'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Navigate to help
                },
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.logout, color: Colors.red),
                title: const Text(
                  '退出登录',
                  style: TextStyle(color: Colors.red),
                ),
                onTap: () => _handleLogout(context),
              ),
            ],
          );
        },
      ),
    );
  }
}
