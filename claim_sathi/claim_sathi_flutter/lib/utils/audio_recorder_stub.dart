import 'dart:async';

abstract class AudioRecorderHelper {
  static Future<bool> isSupported() async => false;
  static Future<void> startRecording({
    String lang = 'hi-IN',
    void Function(String text)? onTranscript,
  }) async {}
  static Future<String?> stopRecording() async => null;
  static bool get isRecording => false;
}
