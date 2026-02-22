import '../config/app_config.dart';

/// API URL constants for Scene Descriptor.
///
/// Uses AppConfig for environment-based configuration.
class ApiUrl {
  /// Base server URL
  static String get baseUrl => AppConfig.serverUrl;

  /// WebRTC signaling endpoint
  static String get offerUrl => AppConfig.offerUrl;

  /// Model switching endpoint
  static String get changeModelUrl => AppConfig.changeModelUrl;

  /// Health check endpoint
  static String get healthUrl => AppConfig.healthUrl;

  // Legacy - kept for compatibility
  static const String quizUrl = '';
}
