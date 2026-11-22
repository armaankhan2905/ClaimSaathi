// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use
import 'dart:async';
import 'dart:html' as html;

class AudioRecorderHelper {
  static html.MediaRecorder? _recorder;
  static html.MediaStream? _stream;
  static final List<html.Blob> _chunks = [];
  static Completer<String?>? _completer;
  static StreamSubscription<html.Event>? _speechSubscription;
  static bool _isRecording = false;

  static bool get isRecording => _isRecording;

  static Future<bool> isSupported() async {
    return html.window.navigator.mediaDevices != null;
  }

  static Future<void> startRecording({
    String lang = 'hi-IN',
    void Function(String text)? onTranscript,
  }) async {
    if (_isRecording) return;
    try {
      // 1. Hook up live speech-to-text recognition via DOM CustomEvent
      _speechSubscription?.cancel();
      if (onTranscript != null) {
        _speechSubscription = html.window.on['claim_saathi_speech_result'].listen((event) {
          final customEvent = event as html.CustomEvent;
          if (customEvent.detail != null) {
            onTranscript(customEvent.detail.toString());
          }
        });
      }

      // Start browser SpeechRecognition
      try {
        final script = html.ScriptElement()
          ..text = 'if(window.claimSaathiSpeech){window.claimSaathiSpeech.start("$lang");}';
        html.document.head?.append(script);
        script.remove();
      } catch (_) {}

      // 2. Start audio media recorder stream
      final stream = await html.window.navigator.mediaDevices?.getUserMedia({
        'audio': true,
      });

      if (stream == null) {
        throw Exception('Microphone permission denied or no audio device found');
      }

      _stream = stream;
      _chunks.clear();

      final options = {'mimeType': 'audio/webm'};
      try {
        _recorder = html.MediaRecorder(stream, options);
      } catch (_) {
        _recorder = html.MediaRecorder(stream);
      }

      _recorder!.addEventListener('dataavailable', (html.Event event) {
        final blobEvent = event as html.BlobEvent;
        if (blobEvent.data != null && blobEvent.data!.size > 0) {
          _chunks.add(blobEvent.data!);
        }
      });

      _recorder!.addEventListener('stop', (html.Event event) {
        if (_chunks.isEmpty) {
          _completer?.complete(null);
          return;
        }

        final blob = html.Blob(_chunks, 'audio/webm');
        final reader = html.FileReader();
        reader.readAsDataUrl(blob);
        reader.onLoadEnd.listen((_) {
          final result = reader.result as String?;
          _completer?.complete(result);
        });
      });

      _recorder!.start(100);
      _isRecording = true;
    } catch (e) {
      _isRecording = false;
      rethrow;
    }
  }

  static Future<String?> stopRecording() async {
    _speechSubscription?.cancel();
    _speechSubscription = null;

    // Stop browser SpeechRecognition
    try {
      final script = html.ScriptElement()
        ..text = 'if(window.claimSaathiSpeech){window.claimSaathiSpeech.stop();}';
      html.document.head?.append(script);
      script.remove();
    } catch (_) {}

    if (!_isRecording || _recorder == null) return null;

    _completer = Completer<String?>();
    _recorder!.stop();
    _isRecording = false;

    // Stop audio tracks
    if (_stream != null) {
      for (final track in _stream!.getTracks()) {
        track.stop();
      }
      _stream = null;
    }

    return _completer!.future;
  }
}
