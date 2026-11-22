// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use
import 'dart:html' as html;
import 'package:flutter/foundation.dart';

class SpeakerHelper {
  static void speak(String text, {String lang = 'hi-IN', VoidCallback? onEnd}) {
    if (html.window.speechSynthesis == null) return;
    html.window.speechSynthesis!.cancel();

    final utterance = html.SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    if (onEnd != null) {
      utterance.addEventListener('end', (html.Event event) {
        onEnd();
      });
    }

    html.window.speechSynthesis!.speak(utterance);
  }

  static void stop() {
    html.window.speechSynthesis?.cancel();
  }

  static bool get isSpeaking => html.window.speechSynthesis?.speaking ?? false;
}
