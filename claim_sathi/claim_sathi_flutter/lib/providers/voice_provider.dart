import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../client.dart';

/// State notifier for managing recorded voice statements.
class VoiceNotifier extends AsyncNotifier<List<VoiceStatement>> {
  @override
  Future<List<VoiceStatement>> build() async {
    return _fetchStatements();
  }

  Future<List<VoiceStatement>> _fetchStatements() async {
    return await client.voice.getVoiceStatements();
  }

  /// Refreshes the statements list from Serverpod.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchStatements());
  }

  /// Saves a voice statement and syncs with PostgreSQL.
  Future<VoiceStatement?> saveStatement(VoiceStatement statement) async {
    state = const AsyncValue.loading();
    try {
      final saved = await client.voice.recordVoiceStatement(statement);
      state = await AsyncValue.guard(() => _fetchStatements());
      return saved;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  /// Deletes a voice statement by database ID.
  Future<void> deleteStatement(int id) async {
    state = const AsyncValue.loading();
    try {
      await client.voice.deleteVoiceStatement(id);
      state = await AsyncValue.guard(() => _fetchStatements());
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

/// Riverpod provider for voice statements.
final voiceProvider =
    AsyncNotifierProvider<VoiceNotifier, List<VoiceStatement>>(
  () => VoiceNotifier(),
);
