// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use
import 'dart:async';
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;
import 'package:flutter/material.dart';

Future<String?> showWebCamCaptureDialog(BuildContext context) async {
  return showDialog<String>(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => const WebCamCaptureDialog(),
  );
}

class WebCamCaptureDialog extends StatefulWidget {
  const WebCamCaptureDialog({super.key});

  @override
  State<WebCamCaptureDialog> createState() => _WebCamCaptureDialogState();
}

class _WebCamCaptureDialogState extends State<WebCamCaptureDialog> {
  html.VideoElement? _videoElement;
  html.MediaStream? _mediaStream;
  String? _viewType;
  bool _isReady = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      html.MediaStream? stream;
      try {
        // First try environment (rear) camera on mobile
        stream = await html.window.navigator.mediaDevices?.getUserMedia({
          'video': {'facingMode': 'environment'},
          'audio': false,
        });
      } catch (_) {
        // Fallback to default camera on laptop/desktop webcams
        stream = await html.window.navigator.mediaDevices?.getUserMedia({
          'video': true,
          'audio': false,
        });
      }

      if (stream == null) {
        setState(() => _error = 'No camera found or permission denied');
        return;
      }

      _mediaStream = stream;
      _videoElement = html.VideoElement()
        ..autoplay = true
        ..muted = true
        ..setAttribute('playsinline', 'true')
        ..srcObject = stream
        ..style.width = '100%'
        ..style.height = '100%'
        ..style.objectFit = 'cover';

      final viewType = 'webcam-view-${DateTime.now().millisecondsSinceEpoch}';
      _viewType = viewType;

      ui_web.platformViewRegistry.registerViewFactory(
        viewType,
        (int viewId) => _videoElement!,
      );

      setState(() => _isReady = true);
    } catch (e) {
      setState(() => _error = 'Camera error: $e');
    }
  }

  void _capture() {
    if (_videoElement == null) return;
    final width = _videoElement!.videoWidth > 0 ? _videoElement!.videoWidth : 640;
    final height = _videoElement!.videoHeight > 0 ? _videoElement!.videoHeight : 480;

    final canvas = html.CanvasElement(width: width, height: height);
    final ctx = canvas.context2D;
    ctx.drawImage(_videoElement!, 0, 0);

    final dataUrl = canvas.toDataUrl('image/jpeg', 0.85);
    final base64Prefix = 'data:image/jpeg;base64,';
    final base64Data = dataUrl.startsWith(base64Prefix)
        ? dataUrl.substring(base64Prefix.length)
        : dataUrl.split(',').last;

    _stopCamera();
    Navigator.of(context).pop(base64Data);
  }

  void _stopCamera() {
    if (_mediaStream != null) {
      for (final track in _mediaStream!.getTracks()) {
        track.stop();
      }
      _mediaStream = null;
    }
  }

  @override
  void dispose() {
    _stopCamera();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 550),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.videocam, color: Colors.blueAccent),
                      SizedBox(width: 8),
                      Text(
                        'Live Camera Scanner',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      _stopCamera();
                      Navigator.of(context).pop(null);
                    },
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 340,
                width: double.infinity,
                child: Stack(
                  children: [
                    Container(
                      width: double.infinity,
                      height: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: _error != null
                          ? Center(
                              child: Padding(
                                padding: const EdgeInsets.all(16),
                                child: Text(
                                  _error!,
                                  style: const TextStyle(color: Colors.redAccent),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            )
                          : !_isReady
                              ? const Center(
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      CircularProgressIndicator(color: Colors.white),
                                      SizedBox(height: 12),
                                      Text(
                                        'Starting camera viewfinder...',
                                        style: TextStyle(color: Colors.white70),
                                      ),
                                    ],
                                  ),
                                )
                              : HtmlElementView(viewType: _viewType!),
                    ),
                    if (_isReady)
                      Center(
                        child: Container(
                          width: 260,
                          height: 200,
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.greenAccent, width: 2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Align(
                            alignment: Alignment.bottomCenter,
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 8),
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.black54,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text(
                                'Align document inside frame',
                                style: TextStyle(color: Colors.white, fontSize: 11),
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    ),
                    onPressed: _isReady ? _capture : null,
                    icon: const Icon(Icons.camera),
                    label: const Text('Capture Photo', style: TextStyle(fontSize: 16)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
