import 'package:flutter/foundation.dart';

abstract class SpeakerHelper {
  static void speak(String text, {String lang = 'hi-IN', VoidCallback? onEnd}) {}
  static void stop() {}
  static bool get isSpeaking => false;
}
