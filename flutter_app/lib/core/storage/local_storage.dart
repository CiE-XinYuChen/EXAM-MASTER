import 'package:shared_preferences/shared_preferences.dart';

/// Local Storage
/// 封装SharedPreferences，提供类型安全的本地存储
class LocalStorage {
  static LocalStorage? _instance;
  static SharedPreferences? _preferences;

  LocalStorage._();

  // Public constructor for dependency injection
  factory LocalStorage() {
    return _instance!;
  }

  static Future<void> init() async {
    _instance ??= LocalStorage._();
    _preferences ??= await SharedPreferences.getInstance();
  }

  static Future<LocalStorage> getInstance() async {
    _instance ??= LocalStorage._();
    _preferences ??= await SharedPreferences.getInstance();
    return _instance!;
  }

  // ==================== String ====================
  Future<bool> setString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setString(key, value);
  }

  Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  // ==================== Int ====================
  Future<bool> setInt(String key, int value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setInt(key, value);
  }

  Future<int?> getInt(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(key);
  }

  // ==================== Double ====================
  Future<bool> setDouble(String key, double value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setDouble(key, value);
  }

  Future<double?> getDouble(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getDouble(key);
  }

  // ==================== Bool ====================
  Future<bool> setBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setBool(key, value);
  }

  Future<bool?> getBool(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(key);
  }

  // ==================== StringList ====================
  Future<bool> setStringList(String key, List<String> value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setStringList(key, value);
  }

  Future<List<String>?> getStringList(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(key);
  }

  // ==================== Remove ====================
  Future<bool> remove(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.remove(key);
  }

  // ==================== Clear ====================
  Future<bool> clear() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.clear();
  }

  // ==================== Contains ====================
  Future<bool> containsKey(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(key);
  }

  // ==================== Get All Keys ====================
  Future<Set<String>> getKeys() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getKeys();
  }

  // ==================== Aliases for save methods ====================
  Future<bool> saveString(String key, String value) => setString(key, value);
  Future<bool> saveInt(String key, int value) => setInt(key, value);
  Future<bool> saveDouble(String key, double value) => setDouble(key, value);
  Future<bool> saveBool(String key, bool value) => setBool(key, value);
  Future<bool> saveStringList(String key, List<String> value) => setStringList(key, value);
}
