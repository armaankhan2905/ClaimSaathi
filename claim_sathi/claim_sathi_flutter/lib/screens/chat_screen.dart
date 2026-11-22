import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/chat_provider.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.25).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleSend() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    final isVoice = ref.read(chatProvider).isListening ||
        ref.read(chatProvider).currentSpokenText.isNotEmpty;

    ref.read(chatProvider.notifier).sendMessage(text, isVoice: isVoice);
    _textController.clear();
    _scrollToBottom();
  }

  Future<void> _toggleVoiceInput() async {
    HapticFeedback.mediumImpact();
    final chatState = ref.read(chatProvider);
    final notifier = ref.read(chatProvider.notifier);

    if (chatState.isListening) {
      await notifier.stopListening();
    } else {
      await notifier.startListening(
        onLiveUpdate: (liveText) {
          if (liveText.isNotEmpty) {
            setState(() {
              _textController.text = liveText;
              _textController.selection = TextSelection.fromPosition(
                TextPosition(offset: _textController.text.length),
              );
            });
          }
        },
      );
    }
  }

  void _showPresetVoicePrompts() {
    final presets = [
      {
        'title': 'Cataract Surgery (Hindi)',
        'prompt': 'क्या मोतियाबिंद सर्जरी का पूरा क्लेम मिलेगा?',
        'lang': 'hi-IN',
      },
      {
        'title': 'Knee Replacement (English)',
        'prompt': "Is my knee replacement covered? I've had this policy since 2022.",
        'lang': 'en-IN',
      },
      {
        'title': 'Room Rent & ICU Cap (Hinglish)',
        'prompt': 'Agar main private room lun to kitna deduction hoga?',
        'lang': 'hi-IN',
      },
      {
        'title': 'Cashless Admission Documents (Hindi)',
        'prompt': 'कैशलेस एडमिट के लिए कौन से दस्तावेज़ चाहिए?',
        'lang': 'hi-IN',
      },
      {
        'title': 'Pre-Existing Disease Waiting (English)',
        'prompt': 'What is the waiting period for pre-existing diabetes or hypertension?',
        'lang': 'en-IN',
      },
      {
        'title': 'Claim Rejection Dispute (Hindi/Legal)',
        'prompt': 'बीमा कंपनी ने क्लेम खारिज कर दिया, ओम्बड्समैन में अपील कैसे करें?',
        'lang': 'hi-IN',
      },
    ];

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.record_voice_over, color: Colors.deepPurpleAccent),
                  const SizedBox(width: 8),
                  const Text(
                    'Instant Voice Prompts (Demo Presets)',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Simulate spoken prompt testing without microphone noise:',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 16),
              Flexible(
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: presets.length,
                  separatorBuilder: (context, index) => const Divider(height: 1),
                  itemBuilder: (ctx, i) {
                    final item = presets[i];
                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: CircleAvatar(
                        backgroundColor: Colors.deepPurple.shade50,
                        child: const Icon(Icons.mic, color: Colors.deepPurpleAccent, size: 20),
                      ),
                      title: Text(
                        item['title']!,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                      subtitle: Text(
                        item['prompt']!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                      ),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () {
                        Navigator.pop(ctx);
                        setState(() {
                          _textController.text = item['prompt']!;
                        });
                        ref
                            .read(chatProvider.notifier)
                            .setLanguage(item['lang']!);
                        _handleSend();
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final notifier = ref.read(chatProvider.notifier);

    // Auto scroll when new messages arrive
    ref.listen(chatProvider.select((s) => s.messages.length), (prev, next) {
      _scrollToBottom();
    });

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.forum, color: Colors.deepPurpleAccent),
            SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Ask ClaimSaathi',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
                ),
                Text(
                  'Arogya Secure Gold (SI ₹5,00,000)',
                  style: TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ],
        ),
        actions: [
          // Language selector
          Container(
            margin: const EdgeInsets.symmetric(vertical: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: BoxDecoration(
              color: Colors.deepPurple.shade50,
              borderRadius: BorderRadius.circular(20),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: chatState.selectedLanguage,
                icon: const Icon(Icons.arrow_drop_down, size: 18),
                style: const TextStyle(fontSize: 12, color: Colors.deepPurple, fontWeight: FontWeight.bold),
                items: const [
                  DropdownMenuItem(value: 'hi-IN', child: Text('🇮🇳 Hindi')),
                  DropdownMenuItem(value: 'en-IN', child: Text('🌐 English')),
                ],
                onChanged: (val) {
                  if (val != null) notifier.setLanguage(val);
                },
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            tooltip: 'Clear Conversation',
            onPressed: () {
              notifier.clearChat();
              _textController.clear();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Active Voice Listening Banner
          if (chatState.isListening) _buildListeningBanner(),

          // Error banner
          if (chatState.errorMessage != null && !chatState.isListening)
            _buildErrorBanner(chatState.errorMessage!),

          // Chat Messages List
          Expanded(
            child: chatState.messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    itemCount: chatState.messages.length + (chatState.isThinking ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == chatState.messages.length && chatState.isThinking) {
                        return _buildThinkingIndicator();
                      }
                      final msg = chatState.messages[index];
                      return _buildMessageBubble(msg, chatState);
                    },
                  ),
          ),

          // Bottom Input Composer with Mic Icon
          _buildComposer(chatState),
        ],
      ),
    );
  }

  Widget _buildListeningBanner() {
    return Container(
      width: double.infinity,
      color: Colors.red.shade50,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Row(
        children: [
          AnimatedBuilder(
            animation: _pulseAnimation,
            builder: (context, child) {
              return Transform.scale(
                scale: _pulseAnimation.value,
                child: Container(
                  width: 12,
                  height: 12,
                  decoration: const BoxDecoration(
                    color: Colors.redAccent,
                    shape: BoxShape.circle,
                  ),
                ),
              );
            },
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '🎙️ Listening to your voice prompt...',
                  style: TextStyle(
                    color: Colors.redAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                Text(
                  'Speak clearly in Hindi or English (tap mic to stop)',
                  style: TextStyle(color: Colors.black54, fontSize: 11),
                ),
              ],
            ),
          ),
          TextButton.icon(
            style: TextButton.styleFrom(
              foregroundColor: Colors.redAccent,
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            ),
            icon: const Icon(Icons.stop, size: 16),
            label: const Text('Stop', style: TextStyle(fontWeight: FontWeight.bold)),
            onPressed: () => ref.read(chatProvider.notifier).stopListening(),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorBanner(String error) {
    return Container(
      width: double.infinity,
      color: Colors.amber.shade50,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          const Icon(Icons.info_outline, size: 18, color: Colors.amber),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              error,
              style: TextStyle(fontSize: 12, color: Colors.amber.shade900),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    final suggestions = [
      "Kya cataract surgery ka poora paisa milega?",
      "Is my knee replacement covered under policy?",
      "Agar main private room lun to kitna deduction hoga?",
      "Which documents do I need for cashless claim?",
      "Waiting period for pre-existing diabetes or BP?",
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.deepPurple.shade50,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.mic_none,
              size: 52,
              color: Colors.deepPurpleAccent,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Ask Your Policy Anything',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Type your question or tap the microphone icon below to speak your prompt in Hindi, English, or Hinglish.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade600, height: 1.4),
          ),
          const SizedBox(height: 28),
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'TRY ASKING (ये पूछकर देखें):',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.8,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          const SizedBox(height: 10),
          ...suggestions.map(
            (s) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: InkWell(
                borderRadius: BorderRadius.circular(10),
                onTap: () {
                  _textController.text = s;
                  _handleSend();
                },
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.help_outline, size: 16, color: Colors.deepPurpleAccent),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          s,
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                        ),
                      ),
                      const Icon(Icons.arrow_forward_ios, size: 12, color: Colors.grey),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildThinkingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.grey.shade100,
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.deepPurpleAccent,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'ClaimSaathi is analyzing policy clauses...',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessageItem msg, ChatState chatState) {
    final isUser = msg.role == MessageRole.user;

    if (isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: const Color(0xFF3F51B5),
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(16),
              topRight: Radius.circular(16),
              bottomLeft: Radius.circular(16),
              bottomRight: Radius.circular(4),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (msg.isVoicePrompt) ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  margin: const EdgeInsets.only(bottom: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.mic, size: 12, color: Colors.white),
                      SizedBox(width: 4),
                      Text(
                        'Voice Spoken',
                        style: TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ],
              Text(
                msg.content,
                style: const TextStyle(color: Colors.white, fontSize: 14.5, height: 1.35),
              ),
            ],
          ),
        ),
      );
    }

    // Assistant Message
    final isSpeakingThis = chatState.activeSpeechMessageId == msg.id;

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 14, right: 36),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(16),
            topRight: Radius.circular(16),
            bottomRight: Radius.circular(16),
            bottomLeft: Radius.circular(4),
          ),
          border: Border.all(color: Colors.grey.shade200),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Chip & Speaker Audio Button
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (msg.verdictLabel != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _verdictColor(msg.verdict).withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: _verdictColor(msg.verdict),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          msg.verdictLabel!,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: _verdictColor(msg.verdict),
                          ),
                        ),
                      ],
                    ),
                  ),
                // Text-to-Speech Button
                IconButton(
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  icon: Icon(
                    isSpeakingThis ? Icons.stop_circle : Icons.volume_up_outlined,
                    size: 22,
                    color: isSpeakingThis ? Colors.redAccent : Colors.teal,
                  ),
                  tooltip: isSpeakingThis ? 'Stop playback' : 'Listen to answer out loud',
                  onPressed: () => ref.read(chatProvider.notifier).toggleSpeechForMessage(msg),
                ),
              ],
            ),
            const SizedBox(height: 10),

            // Content
            Text(
              msg.content,
              style: const TextStyle(fontSize: 14, height: 1.45, color: Colors.black87),
            ),

            // Citations
            if (msg.citations.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...msg.citations.map((c) => _buildCitationBox(c)),
            ],

            // Follow-up Chips
            if (msg.followUps.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: msg.followUps.map((f) {
                  return ActionChip(
                    backgroundColor: Colors.grey.shade50,
                    side: BorderSide(color: Colors.grey.shade300),
                    labelStyle: const TextStyle(fontSize: 12, color: Colors.deepPurple),
                    label: Text(f),
                    onPressed: () {
                      _textController.text = f;
                      _handleSend();
                    },
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCitationBox(PolicyCitation citation) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF9F7F1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE5DECE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.menu_book, size: 14, color: Colors.teal),
              const SizedBox(width: 6),
              Text(
                citation.ref,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.teal,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            citation.quote,
            style: const TextStyle(
              fontSize: 12.5,
              fontStyle: FontStyle.italic,
              color: Color(0xFF3E3A35),
              height: 1.35,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComposer(ChatState chatState) {
    final isListening = chatState.isListening;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            // Preset Voice Prompts Button
            IconButton(
              icon: const Icon(Icons.bolt, color: Colors.amber),
              tooltip: 'Quick Voice Presets (Demo)',
              onPressed: _showPresetVoicePrompts,
            ),

            // Text Input Field
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: isListening ? Colors.redAccent : Colors.transparent,
                    width: 1.5,
                  ),
                ),
                child: TextField(
                  controller: _textController,
                  minLines: 1,
                  maxLines: 4,
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _handleSend(),
                  decoration: InputDecoration(
                    hintText: isListening
                        ? 'Listening to speech...'
                        : 'Ask your policy in English, हिंदी, Hinglish...',
                    hintStyle: TextStyle(
                      fontSize: 13,
                      color: isListening ? Colors.redAccent : Colors.grey.shade500,
                    ),
                    border: InputBorder.none,
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),

            // --- THE MIC ICON BUTTON (Speak the prompt) ---
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: isListening ? _pulseAnimation.value : 1.0,
                  child: child,
                );
              },
              child: Container(
                decoration: BoxDecoration(
                  color: isListening ? Colors.redAccent : Colors.deepPurpleAccent,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (isListening ? Colors.redAccent : Colors.deepPurpleAccent)
                          .withValues(alpha: 0.35),
                      blurRadius: isListening ? 12 : 6,
                      spreadRadius: isListening ? 3 : 1,
                    ),
                  ],
                ),
                child: IconButton(
                  icon: Icon(
                    isListening ? Icons.stop : Icons.mic,
                    color: Colors.white,
                    size: 22,
                  ),
                  tooltip: isListening
                      ? 'Stop speaking (Finish prompt)'
                      : 'Speak prompt via Microphone (Voice Input)',
                  onPressed: _toggleVoiceInput,
                ),
              ),
            ),
            const SizedBox(width: 6),

            // Send Button
            Container(
              decoration: const BoxDecoration(
                color: Color(0xFF3F51B5),
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
                tooltip: 'Send Prompt',
                onPressed: _handleSend,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _verdictColor(VerdictStatus? status) {
    switch (status) {
      case VerdictStatus.likelyCovered:
        return Colors.green.shade700;
      case VerdictStatus.limitApplies:
        return Colors.orange.shade800;
      case VerdictStatus.waitingPeriod:
        return Colors.amber.shade900;
      case VerdictStatus.excluded:
        return Colors.red.shade700;
      case VerdictStatus.needsInfo:
      default:
        return Colors.blue.shade700;
    }
  }
}
