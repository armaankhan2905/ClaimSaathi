import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../client.dart';

/// State notifier for managing the claim audit verdict and legal defense briefing.
class ClaimNotifier extends AsyncNotifier<ClaimVerdict?> {
  @override
  Future<ClaimVerdict?> build() async {
    return _fetchLatest();
  }

  Future<ClaimVerdict?> _fetchLatest() async {
    return await client.claim.getLatestVerdict();
  }

  /// Refreshes the claim audit from Serverpod.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchLatest());
  }

  /// Re-evaluates claim cross-referencing latest camera evidence and voice statements.
  Future<ClaimVerdict?> reEvaluate({String? claimNumber}) async {
    state = const AsyncValue.loading();
    try {
      final verdict = await client.claim.evaluateClaim(claimNumber: claimNumber);
      state = AsyncValue.data(verdict);
      return verdict;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }
}

/// Provider for claim audit verdict.
final claimProvider =
    AsyncNotifierProvider<ClaimNotifier, ClaimVerdict?>(
  () => ClaimNotifier(),
);
