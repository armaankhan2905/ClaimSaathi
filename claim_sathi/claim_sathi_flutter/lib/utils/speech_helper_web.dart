// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use
import 'dart:async';
import 'dart:html' as html;

class SpeechHelper {
  static bool _isListening = false;
  static StreamSubscription? _resultSub;
  static StreamSubscription? _errorSub;
  static StreamSubscription? _endSub;

  static bool isSupported() {
    try {
      return html.window.navigator.mediaDevices != null;
    } catch (_) {
      return false;
    }
  }

  static bool get isListening => _isListening;

  static Future<bool> startListening({
    String lang = 'hi-IN',
    required void Function(String transcript, bool isFinal) onResult,
    void Function(String error)? onError,
    void Function()? onDone,
  }) async {
    try {
      await stopListening();

      _isListening = true;

      // Listen for speech results from the web speech engine
      _resultSub =
          html.window.on['claim_saathi_speech_result'].listen((event) {
        final customEvent = event as html.CustomEvent;
        if (customEvent.detail != null) {
          onResult(customEvent.detail.toString(), false);
        }
      });

      // Listen for speech errors
      _errorSub = html.window.on['claim_saathi_speech_error'].listen((event) {
        final customEvent = event as html.CustomEvent;
        final err = customEvent.detail?.toString() ?? 'Speech recognition error';
        _isListening = false;
        onError?.call(err);
      });

      // Listen for speech end
      _endSub = html.window.on['claim_saathi_speech_end'].listen((event) {
        _isListening = false;
        onDone?.call();
      });

      // Dispatch start
      final script = html.ScriptElement()
        ..text =
            'if(window.claimSaathiSpeech){window.claimSaathiSpeech.start("$lang");}';
      html.document.head?.append(script);
      script.remove();

      return true;
    } catch (e) {
      _isListening = false;
      onError?.call(e.toString());
      return false;
    }
  }

  static Future<void> stopListening() async {
    _isListening = false;
    _resultSub?.cancel();
    _resultSub = null;
    _errorSub?.cancel();
    _errorSub = null;
    _endSub?.cancel();
    _endSub = null;

    try {
      final script = html.ScriptElement()
        ..text =
            'if(window.claimSaathiSpeech){window.claimSaathiSpeech.stop();}';
      html.document.head?.append(script);
      script.remove();
    } catch (_) {}
  }
}
