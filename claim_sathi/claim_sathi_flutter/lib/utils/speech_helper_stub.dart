import 'dart:async';

abstract class SpeechHelper {
  static bool isSupported() => false;
  static bool get isListening => false;

  static Future<bool> startListening({
    String lang = 'hi-IN',
    required void Function(String transcript, bool isFinal) onResult,
    void Function(String error)? onError,
    void Function()? onDone,
  }) async {
    return false;
  }

  static Future<void> stopListening() async {}
}
