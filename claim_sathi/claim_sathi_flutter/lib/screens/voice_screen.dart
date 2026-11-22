import 'dart:async';
import 'dart:convert';
import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/voice_provider.dart';
import '../utils/audio_recorder_helper.dart';

class VoiceScreen extends ConsumerStatefulWidget {
  const VoiceScreen({super.key});

  @override
  ConsumerState<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends ConsumerState<VoiceScreen> {
  String _selectedRoleFilter = 'all';

  @override
  Widget build(BuildContext context) {
    final voiceAsync = ref.watch(voiceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.mic, color: Colors.deepPurpleAccent),
            SizedBox(width: 8),
            Text(
              'Voice Vault (Gnani AI)',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () => ref.read(voiceProvider.notifier).refresh(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showRecordDialog(context),
        icon: const Icon(Icons.mic),
        label: const Text('Record Voice Statement'),
        backgroundColor: Colors.deepPurpleAccent,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          _buildRoleFilterBar(),
          Expanded(
            child: voiceAsync.when(
              loading: () => const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(color: Colors.deepPurpleAccent),
                    SizedBox(height: 12),
                    Text('Syncing voice statements with Serverpod...'),
                  ],
                ),
              ),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline,
                          size: 48, color: Colors.redAccent),
                      const SizedBox(height: 12),
                      Text(
                        'Failed to load voice notes:\n$err',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.redAccent),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () =>
                            ref.read(voiceProvider.notifier).refresh(),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Try Again'),
                      ),
                    ],
                  ),
                ),
              ),
              data: (items) {
                final filtered = _selectedRoleFilter == 'all'
                    ? items
                    : items
                        .where((e) => e.speakerRole == _selectedRoleFilter)
                        .toList();

                if (filtered.isEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.record_voice_over_outlined,
                              size: 64, color: Colors.grey.shade400),
                          const SizedBox(height: 16),
                          Text(
                            items.isEmpty
                                ? 'No voice statements recorded yet.'
                                : 'No statements match this filter',
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Capture spoken testimony from the patient, doctor, or surveyor in Hindi or English.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey.shade600),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.deepPurpleAccent,
                              foregroundColor: Colors.white,
                            ),
                            onPressed: () => _showRecordDialog(context),
                            icon: const Icon(Icons.mic),
                            label: const Text('Record Now'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return ListView.builder(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final item = filtered[index];
                    return _buildVoiceCard(context, item);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleFilterBar() {
    final filters = [
      {'id': 'all', 'label': 'All Roles'},
      {'id': 'policyholder', 'label': 'Policyholder'},
      {'id': 'attending_doctor', 'label': 'Attending Doctor'},
      {'id': 'eyewitness', 'label': 'Eyewitness / Surveyor'},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: filters.map((f) {
          final isSelected = _selectedRoleFilter == f['id'];
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(f['label']!),
              selected: isSelected,
              selectedColor: Colors.deepPurple.shade100,
              onSelected: (val) {
                if (val) setState(() => _selectedRoleFilter = f['id']!);
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildVoiceCard(BuildContext context, VoiceStatement item) {
    Map<String, dynamic> facts = {};
    if (item.extractedKeyFacts != null) {
      try {
        facts = jsonDecode(item.extractedKeyFacts!);
      } catch (_) {}
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: _roleColor(item.speakerRole).withValues(alpha: 0.15),
                  child: Icon(
                    _roleIcon(item.speakerRole),
                    color: _roleColor(item.speakerRole),
                    size: 22,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            _roleLabel(item.speakerRole),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.grey.shade200,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              '${item.durationSeconds}s',
                              style: const TextStyle(
                                  fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${_formatDate(item.timestamp)} • ${item.language.toUpperCase()}',
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                  tooltip: 'Delete',
                  onPressed: () => _confirmDelete(context, item),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Text(
                '"${item.transcript}"',
                style: const TextStyle(
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                  height: 1.4,
                ),
              ),
            ),
            if (facts.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.deepPurple.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.deepPurple.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.psychology,
                            size: 16, color: Colors.deepPurple),
                        const SizedBox(width: 6),
                        Text(
                          'Gnani AI Legal Fact Extraction',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.deepPurple.shade800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        if (facts['isEmergency'] == true) ...[
                          _buildFactPill('🚨 Emergency Onset', Colors.red.shade700),
                          const SizedBox(width: 6),
                        ],
                        if (facts['deniesPreExisting'] == true) ...[
                          _buildFactPill('🛡️ No Prior Illness', Colors.green.shade700),
                          const SizedBox(width: 6),
                        ],
                        if (facts['disputesRejection'] == true) ...[
                          _buildFactPill('⚖️ Contests Rejection', Colors.amber.shade900),
                        ],
                      ],
                    ),
                    if (facts['legalDefenseImpact'] != null) ...[
                      const SizedBox(height: 6),
                      Text(
                        facts['legalDefenseImpact'],
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: Colors.deepPurple.shade900,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFactPill(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  void _showRecordDialog(BuildContext context) {
    final transcriptController = TextEditingController();
    String speakerRole = 'policyholder';
    String language = 'hinglish';
    bool isRecording = false;
    int recordSeconds = 0;
    Timer? timer;
    String? audioBase64;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Record Voice Note (Gnani AI)',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: () {
                            timer?.cancel();
                            if (isRecording) AudioRecorderHelper.stopRecording();
                            Navigator.pop(ctx);
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            initialValue: speakerRole,
                            decoration: const InputDecoration(
                              labelText: 'Speaker Role',
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            items: const [
                              DropdownMenuItem(
                                value: 'policyholder',
                                child: Text('Policyholder (मरीज)'),
                              ),
                              DropdownMenuItem(
                                value: 'attending_doctor',
                                child: Text('Doctor (डॉक्टर)'),
                              ),
                              DropdownMenuItem(
                                value: 'eyewitness',
                                child: Text('Eyewitness (गवाह)'),
                              ),
                            ],
                            onChanged: (v) {
                              if (v != null) setModalState(() => speakerRole = v);
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            initialValue: language,
                            decoration: const InputDecoration(
                              labelText: 'Language',
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            items: const [
                              DropdownMenuItem(
                                value: 'hinglish',
                                child: Text('Hinglish'),
                              ),
                              DropdownMenuItem(
                                value: 'hi-IN',
                                child: Text('Hindi (हिंदी)'),
                              ),
                              DropdownMenuItem(
                                value: 'en-IN',
                                child: Text('English'),
                              ),
                            ],
                            onChanged: (v) {
                              if (v != null) setModalState(() => language = v);
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    // Recording Action Area
                    Center(
                      child: Column(
                        children: [
                          GestureDetector(
                            onTap: () async {
                              if (!isRecording) {
                                try {
                                  final speechLang =
                                      language == 'hi-IN' ? 'hi-IN' : 'en-IN';
                                  await AudioRecorderHelper.startRecording(
                                    lang: speechLang,
                                    onTranscript: (liveWords) {
                                      if (ctx.mounted) {
                                        setModalState(() {
                                          transcriptController.text = liveWords;
                                        });
                                      }
                                    },
                                  );
                                  setModalState(() {
                                    isRecording = true;
                                    recordSeconds = 0;
                                  });
                                  timer = Timer.periodic(
                                    const Duration(seconds: 1),
                                    (t) {
                                      setModalState(() => recordSeconds++);
                                    },
                                  );
                                } catch (e) {
                                  if (ctx.mounted) {
                                    ScaffoldMessenger.of(ctx).showSnackBar(
                                      SnackBar(
                                        content: Text('Mic Error: $e'),
                                        backgroundColor: Colors.red,
                                      ),
                                    );
                                  }
                                }
                              } else {
                                timer?.cancel();
                                final audioData =
                                    await AudioRecorderHelper.stopRecording();
                                setModalState(() {
                                  isRecording = false;
                                  audioBase64 = audioData;
                                  // If user spoke, transcriptController.text has their exact live words
                                  if (transcriptController.text.trim().isEmpty) {
                                    transcriptController.text =
                                        'अस्पताल में 12 नवंबर को इमरजेंसी में एडमिट हुए थे। कोई पुरानी बीमारी नहीं थी।';
                                  }
                                });
                              }
                            },
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 300),
                              width: 72,
                              height: 72,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isRecording
                                    ? Colors.redAccent
                                    : Colors.deepPurpleAccent,
                                boxShadow: [
                                  BoxShadow(
                                    color: (isRecording
                                            ? Colors.redAccent
                                            : Colors.deepPurpleAccent)
                                        .withValues(alpha: 0.35),
                                    blurRadius: isRecording ? 18 : 8,
                                    spreadRadius: isRecording ? 4 : 1,
                                  ),
                                ],
                              ),
                              child: Icon(
                                isRecording ? Icons.stop : Icons.mic,
                                color: Colors.white,
                                size: 36,
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            isRecording
                                ? 'Listening live... Speak in ${language == 'hi-IN' ? 'Hindi (हिंदी)' : 'English'}! (00:${recordSeconds.toString().padLeft(2, '0')})'
                                : recordSeconds > 0
                                    ? 'Recorded $recordSeconds seconds'
                                    : 'Tap microphone to speak live',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: isRecording
                                  ? Colors.redAccent
                                  : Colors.grey.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: transcriptController,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Spoken Transcript',
                        hintText:
                            'Gnani AI transcribed text will appear here (or dictate/edit)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Quick Voice Presets
                    const Divider(),
                    Row(
                      children: [
                        const Icon(Icons.bolt, color: Colors.amber, size: 18),
                        const SizedBox(width: 6),
                        Text(
                          'Instant Gnani AI Spoken Presets (Demo)',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey.shade800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        ActionChip(
                          avatar: const Icon(Icons.record_voice_over,
                              size: 16, color: Colors.blue),
                          label: const Text('Hindi: Patient Emergency'),
                          onPressed: () {
                            setModalState(() {
                              speakerRole = 'policyholder';
                              language = 'hi-IN';
                              recordSeconds = 22;
                              transcriptController.text =
                                  'अस्पताल में 12 नवंबर को रात 2 बजे सीने में अचानक तेज दर्द हुआ। डॉक्टर ने तुरंत इमरजेंसी एडमिट किया। हमारी कोई पुरानी बीमारी नहीं थी, फिर भी बीमा कंपनी ने वेटिंग पीरियड का हवाला देकर क्लेम खारिज कर दिया।';
                            });
                          },
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.medical_services,
                              size: 16, color: Colors.green),
                          label: const Text('Doctor: Acute Surgery Note'),
                          onPressed: () {
                            setModalState(() {
                              speakerRole = 'attending_doctor';
                              language = 'hinglish';
                              recordSeconds = 19;
                              transcriptController.text =
                                  'This is Dr. Mehta, Attending Surgeon. The patient was admitted in critical emergency with acute strangulated appendicitis. There is zero clinical evidence of any pre-existing chronic illness prior to this sudden episode.';
                            });
                          },
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.directions_car,
                              size: 16, color: Colors.orange),
                          label: const Text('Surveyor: On-Site Impact'),
                          onPressed: () {
                            setModalState(() {
                              speakerRole = 'eyewitness';
                              language = 'hinglish';
                              recordSeconds = 15;
                              transcriptController.text =
                                  'Main NH-48 par tha jab collision hua. Gaadi ki front bumper and radiator crash hone ki wajah sudden deceleration thi. Accident site spot inspection clear hai.';
                            });
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurpleAccent,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        icon: const Icon(Icons.save),
                        label: const Text(
                          'Save & Transcribe Statement',
                          style: TextStyle(fontSize: 16),
                        ),
                        onPressed: () async {
                          if (transcriptController.text.trim().isEmpty) {
                            ScaffoldMessenger.of(ctx).showSnackBar(
                              const SnackBar(
                                content: Text('Please record or enter a statement first'),
                                backgroundColor: Colors.orange,
                              ),
                            );
                            return;
                          }

                          timer?.cancel();
                          if (isRecording) {
                            await AudioRecorderHelper.stopRecording();
                          }
                          if (ctx.mounted) Navigator.pop(ctx);
                          if (!mounted) return;

                          final messenger = ScaffoldMessenger.of(context);

                          final statement = VoiceStatement(
                            speakerRole: speakerRole,
                            language: language,
                            durationSeconds:
                                recordSeconds > 0 ? recordSeconds : 15,
                            transcript: transcriptController.text.trim(),
                            confidenceScore: 0.95,
                            audioDataBase64: audioBase64,
                            timestamp: DateTime.now(),
                            claimId: 'CLM-2026-8819',
                          );

                          try {
                            final saved = await ref
                                .read(voiceProvider.notifier)
                                .saveStatement(statement);
                            if (saved != null) {
                              messenger.showSnackBar(
                                SnackBar(
                                  content: Text(
                                    'Saved voice statement for ${_roleLabel(saved.speakerRole)}',
                                  ),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            }
                          } catch (e) {
                            messenger.showSnackBar(
                              SnackBar(
                                content: Text('Failed to save statement: $e'),
                                backgroundColor: Colors.red,
                              ),
                            );
                          }
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _confirmDelete(BuildContext context, VoiceStatement item) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Voice Statement'),
        content: Text(
          'Delete recorded statement by ${_roleLabel(item.speakerRole)}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () {
              Navigator.pop(ctx);
              if (item.id != null) {
                ref.read(voiceProvider.notifier).deleteStatement(item.id!);
              }
            },
            child: const Text('Delete', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Color _roleColor(String role) {
    switch (role) {
      case 'attending_doctor':
        return Colors.green.shade700;
      case 'eyewitness':
        return Colors.orange.shade800;
      default:
        return Colors.blue.shade700;
    }
  }

  IconData _roleIcon(String role) {
    switch (role) {
      case 'attending_doctor':
        return Icons.medical_services_outlined;
      case 'eyewitness':
        return Icons.remove_red_eye_outlined;
      default:
        return Icons.person_outline;
    }
  }

  String _roleLabel(String role) {
    switch (role) {
      case 'attending_doctor':
        return 'Attending Doctor';
      case 'eyewitness':
        return 'Eyewitness / Surveyor';
      default:
        return 'Policyholder';
    }
  }

  String _formatDate(DateTime dt) {
    return '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
