/// Application configuration for Scene Descriptor.
///
/// Contains environment-based configuration for API endpoints
/// and other application settings.
class AppConfig {
  // Development server URL - update this to your local server IP
  static const String _devServerUrl = "http://192.168.1.65:8080";

  // Production server URL - update when deploying
  static const String _prodServerUrl = "https://api.scenedescriptor.com";

  /// Check if running in production mode
  static const bool isProduction = bool.fromEnvironment('dart.vm.product');

  /// Get the appropriate server URL based on environment
  static String get serverUrl => isProduction ? _prodServerUrl : _devServerUrl;

  /// WebRTC offer endpoint
  static String get offerUrl => "$serverUrl/offer";

  /// Model switching endpoint
  static String get changeModelUrl => "$serverUrl/change_model";

  /// Health check endpoint
  static String get healthUrl => "$serverUrl/health";

  // Application settings
  static const int connectionTimeoutSeconds = 30;
  static const int captionDisplayDurationMs = 5000;

  // Video constraints
  static const int videoWidth = 224;
  static const int videoHeight = 224;
  static const int frameRate = 30;

  // TTS settings
  static const String ttsLanguage = 'en-US';
  static const double ttsPitch = 1.0;
  static const double ttsVolume = 1.0;
  static const double ttsSpeechRate = 0.2;
}
