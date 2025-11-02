import 'package:connectivity_plus/connectivity_plus.dart';

/// Network Info
/// 网络连接状态检测
class NetworkInfo {
  final Connectivity _connectivity = Connectivity();

  /// 检查是否有网络连接
  Future<bool> get isConnected async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  /// 获取当前连接类型
  Future<ConnectivityResult> get connectionType async {
    return await _connectivity.checkConnectivity();
  }

  /// 监听网络状态变化
  Stream<ConnectivityResult> get onConnectivityChanged {
    return _connectivity.onConnectivityChanged;
  }

  /// 检查是否是WiFi连接
  Future<bool> get isWifi async {
    final result = await _connectivity.checkConnectivity();
    return result == ConnectivityResult.wifi;
  }

  /// 检查是否是移动网络
  Future<bool> get isMobile async {
    final result = await _connectivity.checkConnectivity();
    return result == ConnectivityResult.mobile;
  }

  /// 获取连接类型的友好名称
  String getConnectionTypeName(ConnectivityResult result) {
    switch (result) {
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.mobile:
        return '移动网络';
      case ConnectivityResult.ethernet:
        return '以太网';
      case ConnectivityResult.bluetooth:
        return '蓝牙';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.none:
        return '无网络';
      default:
        return '未知';
    }
  }
}
