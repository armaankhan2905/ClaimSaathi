import 'dart:convert';
import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../client.dart';

/// State notifier for managing scanned evidence items.
class EvidenceNotifier extends AsyncNotifier<List<EvidenceMedia>> {
  final _picker = ImagePicker();

  @override
  Future<List<EvidenceMedia>> build() async {
    return _fetchEvidence();
  }

  Future<List<EvidenceMedia>> _fetchEvidence() async {
    return await client.evidence.getEvidenceList();
  }

  /// Refreshes the evidence list.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchEvidence());
  }

  /// Captures a photo using the Camera or Gallery, encodes it, and uploads to Serverpod.
  Future<EvidenceMedia?> captureAndUpload({
    required String title,
    required String category,
    ImageSource source = ImageSource.camera,
    String? notes,
  }) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        maxWidth: 1600,
        maxHeight: 1600,
        imageQuality: 85,
      );

      if (picked == null) return null;

      final bytes = await picked.readAsBytes();
      final base64String = base64Encode(bytes);

      state = const AsyncValue.loading();

      final newEvidence = EvidenceMedia(
        title: title.trim().isEmpty ? 'Scanned Document' : title.trim(),
        category: category,
        mediaType: 'image',
        dataBase64: base64String,
        notes: notes,
        timestamp: DateTime.now(),
      );

      final uploaded = await client.evidence.uploadEvidence(newEvidence);

      // Refresh list
      state = await AsyncValue.guard(() => _fetchEvidence());
      return uploaded;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  /// Uploads base64 encoded evidence data directly (e.g. from WebCam or Sample Presets).
  Future<EvidenceMedia?> uploadDirect({
    required String title,
    required String category,
    required String base64Data,
    String? notes,
  }) async {
    state = const AsyncValue.loading();
    try {
      final newEvidence = EvidenceMedia(
        title: title.trim().isEmpty ? 'Scanned Document' : title.trim(),
        category: category,
        mediaType: 'image',
        dataBase64: base64Data,
        notes: notes,
        timestamp: DateTime.now(),
      );

      final uploaded = await client.evidence.uploadEvidence(newEvidence);
      state = await AsyncValue.guard(() => _fetchEvidence());
      return uploaded;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  /// Deletes an evidence item by ID.
  Future<void> deleteEvidence(int id) async {
    state = const AsyncValue.loading();
    try {
      await client.evidence.deleteEvidence(id);
      state = await AsyncValue.guard(() => _fetchEvidence());
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

/// Provider for accessing and modifying the list of evidence.
final evidenceProvider =
    AsyncNotifierProvider<EvidenceNotifier, List<EvidenceMedia>>(
  () => EvidenceNotifier(),
);
