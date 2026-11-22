import 'dart:convert';
import 'package:claim_sathi_client/claim_sathi_client.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/evidence_provider.dart';
import '../utils/camera_helper.dart';
import '../utils/sample_data.dart';

class EvidenceScreen extends ConsumerStatefulWidget {
  const EvidenceScreen({super.key});

  @override
  ConsumerState<EvidenceScreen> createState() => _EvidenceScreenState();
}

class _EvidenceScreenState extends ConsumerState<EvidenceScreen> {
  String _selectedFilter = 'all';

  @override
  Widget build(BuildContext context) {
    final evidenceAsync = ref.watch(evidenceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.shield_outlined, color: Colors.blueAccent),
            SizedBox(width: 8),
            Text(
              'Evidence Vault',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () => ref.read(evidenceProvider.notifier).refresh(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCaptureDialog(context),
        icon: const Icon(Icons.camera_alt),
        label: const Text('Scan Evidence'),
        backgroundColor: Colors.blueAccent,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          _buildFilterBar(),
          Expanded(
            child: evidenceAsync.when(
              loading: () => const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('Syncing evidence with Serverpod...'),
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
                        'Failed to load evidence:\n$err',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.redAccent),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () =>
                            ref.read(evidenceProvider.notifier).refresh(),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Try Again'),
                      ),
                    ],
                  ),
                ),
              ),
              data: (items) {
                final filtered = _selectedFilter == 'all'
                    ? items
                    : items
                        .where((e) => e.category == _selectedFilter)
                        .toList();

                if (filtered.isEmpty) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.camera_enhance_outlined,
                              size: 64, color: Colors.grey.shade400),
                          const SizedBox(height: 16),
                          Text(
                            items.isEmpty
                                ? 'No evidence scanned yet.'
                                : 'No items match "$_selectedFilter"',
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Use your camera to scan hospital bills, vehicle damage, or rejection letters.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey.shade600),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            onPressed: () => _showCaptureDialog(context),
                            icon: const Icon(Icons.camera_alt),
                            label: const Text('Scan Now'),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final item = filtered[index];
                    return _buildEvidenceCard(context, item);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar() {
    final filters = [
      {'id': 'all', 'label': 'All'},
      {'id': 'rejection_letter', 'label': 'Rejection Letter'},
      {'id': 'hospital_bill', 'label': 'Hospital Bill'},
      {'id': 'vehicle_damage', 'label': 'Vehicle Damage'},
      {'id': 'other', 'label': 'Other'},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: filters.map((f) {
          final isSelected = _selectedFilter == f['id'];
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(f['label']!),
              selected: isSelected,
              onSelected: (val) {
                if (val) setState(() => _selectedFilter = f['id']!);
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildEvidenceCard(BuildContext context, EvidenceMedia item) {
    ImageProvider? imageProvider;
    try {
      if (item.dataBase64.isNotEmpty) {
        imageProvider = MemoryImage(base64Decode(item.dataBase64));
      }
    } catch (_) {
      imageProvider = null;
    }

    Map<String, dynamic> docData = {};
    if (item.notes != null && item.notes!.trim().startsWith('{')) {
      try {
        docData = jsonDecode(item.notes!);
      } catch (_) {}
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _showDetailDialog(context, item, imageProvider, docData),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey.shade200,
                      child: imageProvider != null
                          ? Image(image: imageProvider, fit: BoxFit.cover)
                          : const Icon(Icons.insert_drive_file, color: Colors.blueGrey),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.title,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: _categoryColor(item.category).withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                _categoryLabel(item.category),
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: _categoryColor(item.category),
                                ),
                              ),
                            ),
                            if (docData['claimAmount'] != null) ...[
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade50,
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(color: Colors.green.shade200),
                                ),
                                child: Text(
                                  docData['claimAmount'],
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green.shade800,
                                  ),
                                ),
                              ),
                            ],
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _formatDate(item.timestamp),
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
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
              if (docData.isNotEmpty) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.shade100),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.psychology, size: 16, color: Colors.blueAccent),
                          const SizedBox(width: 6),
                          Text(
                            docData['insurer'] ?? docData['hospital'] ?? docData['docType'] ?? 'Document Intelligence',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.blue.shade900,
                            ),
                          ),
                        ],
                      ),
                      if (docData['citedClause'] != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          '⚠️ ${docData['citedClause']}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Colors.red.shade900,
                          ),
                        ),
                      ],
                      if (docData['diagnosis'] != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          '🩺 ${docData['diagnosis']}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo.shade900,
                          ),
                        ),
                      ],
                      if (docData['legalValidity'] != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          docData['legalValidity'],
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                            color: Colors.blue.shade900,
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
      ),
    );
  }

  void _showCaptureDialog(BuildContext context) {
    final titleController = TextEditingController();
    final notesController = TextEditingController();
    String category = 'rejection_letter';

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
                          'Add Claim Evidence',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: () => Navigator.pop(ctx),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: 'Evidence Title (Optional)',
                        hintText: 'e.g. Star Health Rejection Notice',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: category,
                      decoration: const InputDecoration(
                        labelText: 'Evidence Category',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'rejection_letter',
                          child: Text('Rejection Letter'),
                        ),
                        DropdownMenuItem(
                          value: 'hospital_bill',
                          child: Text('Hospital Bill / Summary'),
                        ),
                        DropdownMenuItem(
                          value: 'vehicle_damage',
                          child: Text('Vehicle Damage Photo'),
                        ),
                        DropdownMenuItem(
                          value: 'other',
                          child: Text('Other Evidence'),
                        ),
                      ],
                      onChanged: (v) {
                        if (v != null) setModalState(() => category = v);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: notesController,
                      maxLines: 2,
                      decoration: const InputDecoration(
                        labelText: 'Notes (Optional)',
                        hintText: 'e.g. Insurer citing 36-month waiting period',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blueAccent,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                            icon: const Icon(Icons.videocam),
                            label: const Text('Open Live Camera'),
                            onPressed: () async {
                              Navigator.pop(ctx);
                              final capturedB64 =
                                  await showWebCamCaptureDialog(context);
                              if (capturedB64 != null && mounted) {
                                await _uploadDirectBase64(
                                  titleController.text,
                                  category,
                                  notesController.text,
                                  capturedB64,
                                );
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                            icon: const Icon(Icons.file_upload_outlined),
                            label: const Text('Upload File'),
                            onPressed: () async {
                              final picker = ImagePicker();
                              final picked = await picker.pickImage(
                                source: ImageSource.gallery,
                                maxWidth: 1600,
                                maxHeight: 1600,
                                imageQuality: 85,
                              );
                              if (picked != null) {
                                if (ctx.mounted) Navigator.pop(ctx);
                                final bytes = await picked.readAsBytes();
                                final b64 = base64Encode(bytes);
                                if (mounted) {
                                  await _uploadDirectBase64(
                                    titleController.text,
                                    category,
                                    notesController.text,
                                    b64,
                                  );
                                }
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const Divider(),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.bolt, color: Colors.amber, size: 20),
                        const SizedBox(width: 6),
                        Text(
                          'Quick Test Presets (Instant Hackathon Demo)',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey.shade800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        ActionChip(
                          avatar: const Icon(Icons.description, size: 16, color: Colors.red),
                          label: const Text('Star Health Rejection'),
                          onPressed: () async {
                            Navigator.pop(ctx);
                            await _uploadDirectBase64(
                              'Star Health Repudiation Letter',
                              'rejection_letter',
                              'Claim rejected under Clause 4.2 waiting period for hypertension.',
                              SampleEvidenceData.rejectionLetter,
                            );
                          },
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.local_hospital, size: 16, color: Colors.green),
                          label: const Text('Fortis Hospital Bill'),
                          onPressed: () async {
                            Navigator.pop(ctx);
                            await _uploadDirectBase64(
                              'Fortis Hospital Discharge Summary',
                              'hospital_bill',
                              'Emergency acute appendicitis surgery bill for INR 1,45,200.',
                              SampleEvidenceData.hospitalBill,
                            );
                          },
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.directions_car, size: 16, color: Colors.orange),
                          label: const Text('Car Bumper Damage'),
                          onPressed: () async {
                            Navigator.pop(ctx);
                            await _uploadDirectBase64(
                              'Motor On-Site Survey Report',
                              'vehicle_damage',
                              'Front bumper and radiator collision damage on NH-48.',
                              SampleEvidenceData.vehicleDamage,
                            );
                          },
                        ),
                      ],
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

  Future<void> _uploadDirectBase64(
    String title,
    String category,
    String notes,
    String base64Data,
  ) async {
    try {
      final uploaded = await ref.read(evidenceProvider.notifier).uploadDirect(
            title: title.isEmpty ? _categoryLabel(category) : title,
            category: category,
            base64Data: base64Data,
            notes: notes.isEmpty ? null : notes,
          );
      if (uploaded != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Successfully uploaded: ${uploaded.title}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showDetailDialog(
      BuildContext context,
      EvidenceMedia item,
      ImageProvider? imageProvider,
      Map<String, dynamic> docData) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(item.title),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (imageProvider != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image(image: imageProvider),
                ),
              const SizedBox(height: 12),
              Text('Category: ${_categoryLabel(item.category)}',
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              Text('Timestamp: ${_formatDate(item.timestamp)}'),
              if (docData.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Divider(),
                const Text('Extracted Document Intelligence:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 8),
                if (docData['insurer'] != null)
                  Text('🏢 Insurer: ${docData['insurer']}'),
                if (docData['hospital'] != null)
                  Text('🏥 Hospital: ${docData['hospital']}'),
                if (docData['claimNumber'] != null || docData['claimId'] != null)
                  Text('📄 Claim ID: ${docData['claimNumber'] ?? docData['claimId']}'),
                if (docData['claimAmount'] != null)
                  Text('💰 Claim Amount: ${docData['claimAmount']}',
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                if (docData['citedClause'] != null)
                  Text('⚠️ Cited Clause: ${docData['citedClause']}',
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
                if (docData['diagnosis'] != null)
                  Text('🩺 Diagnosis: ${docData['diagnosis']}'),
                if (docData['legalValidity'] != null) ...[
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      '⚖️ Legal Status: ${docData['legalValidity']}',
                      style: TextStyle(fontSize: 12, color: Colors.blue.shade900),
                    ),
                  ),
                ],
              ] else if (item.notes != null) ...[
                const SizedBox(height: 8),
                Text('Notes: ${item.notes}'),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _confirmDelete(BuildContext context, EvidenceMedia item) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Evidence'),
        content: Text('Are you sure you want to delete "${item.title}"?'),
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
                ref.read(evidenceProvider.notifier).deleteEvidence(item.id!);
              }
            },
            child: const Text('Delete', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  Color _categoryColor(String category) {
    switch (category) {
      case 'rejection_letter':
        return Colors.red.shade700;
      case 'hospital_bill':
        return Colors.green.shade700;
      case 'vehicle_damage':
        return Colors.amber.shade800;
      default:
        return Colors.blue.shade700;
    }
  }

  String _categoryLabel(String category) {
    switch (category) {
      case 'rejection_letter':
        return 'Rejection Letter';
      case 'hospital_bill':
        return 'Hospital Bill';
      case 'vehicle_damage':
        return 'Vehicle Damage';
      default:
        return 'Other Evidence';
    }
  }

  String _formatDate(DateTime dt) {
    return '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
