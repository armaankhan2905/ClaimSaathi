import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/claim_provider.dart';
import '../utils/speaker_helper.dart';

class DefenseScreen extends ConsumerStatefulWidget {
  const DefenseScreen({super.key});

  @override
  ConsumerState<DefenseScreen> createState() => _DefenseScreenState();
}

class _DefenseScreenState extends ConsumerState<DefenseScreen> {
  String _selectedLanguage = 'hi-IN'; // 'hi-IN' or 'en-IN'
  bool _isPlaying = false;

  @override
  void dispose() {
    SpeakerHelper.stop();
    super.dispose();
  }

  void _toggleSpeech(ClaimVerdict verdict) {
    if (_isPlaying) {
      SpeakerHelper.stop();
      setState(() => _isPlaying = false);
    } else {
      final textToSpeak = _selectedLanguage == 'hi-IN'
          ? verdict.spokenDefenseHindi
          : verdict.spokenDefenseEnglish;

      setState(() => _isPlaying = true);

      SpeakerHelper.speak(
        textToSpeak,
        lang: _selectedLanguage,
        onEnd: () {
          if (mounted) setState(() => _isPlaying = false);
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final claimAsync = ref.watch(claimProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.volume_up, color: Colors.teal),
            SizedBox(width: 8),
            Text(
              'Speaker Defense Briefing',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.auto_awesome),
            tooltip: 'Re-Evaluate with AI',
            onPressed: () => ref.read(claimProvider.notifier).reEvaluate(),
          ),
        ],
      ),
      body: claimAsync.when(
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(color: Colors.teal),
              SizedBox(height: 12),
              Text('Reconciling Camera & Voice Evidence...'),
            ],
          ),
        ),
        error: (err, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
                const SizedBox(height: 12),
                Text(
                  'Failed to compute claim verdict:\n$err',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.redAccent),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () => ref.read(claimProvider.notifier).refresh(),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Try Again'),
                ),
              ],
            ),
          ),
        ),
        data: (verdict) {
          if (verdict == null) {
            return const Center(child: Text('No claim verdict available.'));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSpeakerCard(verdict),
                const SizedBox(height: 16),
                _buildVerdictCard(verdict),
                const SizedBox(height: 16),
                _buildEvidenceReconciliationCard(verdict),
                const SizedBox(height: 16),
                _buildGrievanceNoticeButton(verdict),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSpeakerCard(ClaimVerdict verdict) {
    final speechText = _selectedLanguage == 'hi-IN'
        ? verdict.spokenDefenseHindi
        : verdict.spokenDefenseEnglish;

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.teal.shade700, Colors.teal.shade900],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isPlaying ? Icons.record_voice_over : Icons.volume_up,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Device Speaker Briefing',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Spoken rights & defense readback',
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Language selector tabs
            Row(
              children: [
                ChoiceChip(
                  label: const Text('Hindi (हिंदी) 🇮🇳'),
                  selected: _selectedLanguage == 'hi-IN',
                  selectedColor: Colors.amber,
                  backgroundColor: Colors.white.withValues(alpha: 0.15),
                  labelStyle: TextStyle(
                    color: _selectedLanguage == 'hi-IN'
                        ? Colors.black87
                        : Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                  onSelected: (val) {
                    if (val) {
                      SpeakerHelper.stop();
                      setState(() {
                        _selectedLanguage = 'hi-IN';
                        _isPlaying = false;
                      });
                    }
                  },
                ),
                const SizedBox(width: 8),
                ChoiceChip(
                  label: const Text('English 🌐'),
                  selected: _selectedLanguage == 'en-IN',
                  selectedColor: Colors.amber,
                  backgroundColor: Colors.white.withValues(alpha: 0.15),
                  labelStyle: TextStyle(
                    color: _selectedLanguage == 'en-IN'
                        ? Colors.black87
                        : Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                  onSelected: (val) {
                    if (val) {
                      SpeakerHelper.stop();
                      setState(() {
                        _selectedLanguage = 'en-IN';
                        _isPlaying = false;
                      });
                    }
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
              ),
              child: Text(
                '"$speechText"',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  height: 1.5,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isPlaying ? Colors.redAccent : Colors.amber,
                  foregroundColor: _isPlaying ? Colors.white : Colors.black87,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                icon: Icon(_isPlaying ? Icons.stop : Icons.play_arrow),
                label: Text(
                  _isPlaying
                      ? 'Stop Audio Playback'
                      : 'Play Over Speaker (आवाज़ में सुनें)',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                onPressed: () => _toggleSpeech(verdict),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerdictCard(ClaimVerdict verdict) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.red.shade100,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.gavel, size: 16, color: Colors.red.shade800),
                      const SizedBox(width: 6),
                      Text(
                        'AUDIT VERDICT: OVERTURN REJECTION',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.red.shade900,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Recoverable Claim Payout',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    Text(
                      '₹${verdict.claimedAmount.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      'Claim Tracking No.',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    Text(
                      verdict.claimNumber,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Divider(),
            const SizedBox(height: 10),
            Text(
              'Unlawful Clause Invoked by Insurer:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 13,
                color: Colors.grey.shade800,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                verdict.disputedClause,
                style: const TextStyle(fontSize: 13, color: Colors.black87),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Statutory IRDAI Protection Basis:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 13,
                color: Colors.grey.shade800,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                verdict.legalBasis,
                style: TextStyle(fontSize: 13, color: Colors.blue.shade900),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEvidenceReconciliationCard(ClaimVerdict verdict) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.hub, color: Colors.indigo),
                SizedBox(width: 8),
                Text(
                  'Multi-Modal Sense Reconciliation',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        const Icon(Icons.camera_alt, color: Colors.blueAccent),
                        const SizedBox(height: 6),
                        Text(
                          '${verdict.evidenceCount} Scanned Proofs',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const Text(
                          'Discharge Summary & Bills',
                          style: TextStyle(fontSize: 11, color: Colors.black54),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.deepPurple.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        const Icon(Icons.mic, color: Colors.deepPurpleAccent),
                        const SizedBox(height: 6),
                        Text(
                          '${verdict.voiceStatementsCount} Voice Proofs',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const Text(
                          'Dr. Mehta + Patient Statement',
                          style: TextStyle(fontSize: 11, color: Colors.black54),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGrievanceNoticeButton(ClaimVerdict verdict) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 14),
          side: const BorderSide(color: Colors.teal, width: 1.5),
        ),
        icon: const Icon(Icons.description_outlined, color: Colors.teal),
        label: const Text(
          'View IRDAI Formal Grievance Notice',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.teal),
        ),
        onPressed: () => _showGrievanceNoticeModal(context, verdict),
      ),
    );
  }

  void _showGrievanceNoticeModal(BuildContext context, ClaimVerdict verdict) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.85,
          maxChildSize: 0.95,
          minChildSize: 0.5,
          expand: false,
          builder: (_, controller) {
            return Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'IRDAI Grievance Notice',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      Row(
                        children: [
                          IconButton(
                            icon: const Icon(Icons.copy),
                            tooltip: 'Copy Notice Text',
                            onPressed: () {
                              Clipboard.setData(ClipboardData(
                                  text: verdict.grievanceLetterMarkdown));
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Notice text copied to clipboard!'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            },
                          ),
                          IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () => Navigator.pop(ctx),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const Divider(),
                  Expanded(
                    child: SingleChildScrollView(
                      controller: controller,
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade100,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: SelectableText(
                          verdict.grievanceLetterMarkdown,
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 13,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
