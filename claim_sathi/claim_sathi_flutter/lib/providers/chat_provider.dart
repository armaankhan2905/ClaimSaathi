import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/speaker_helper.dart';
import '../utils/speech_helper.dart';

enum MessageRole { user, assistant }

enum VerdictStatus {
  likelyCovered,
  waitingPeriod,
  limitApplies,
  needsInfo,
  excluded,
}

class PolicyCitation {
  final String ref;
  final String title;
  final String quote;

  const PolicyCitation({
    required this.ref,
    required this.title,
    required this.quote,
  });
}

class ChatMessageItem {
  final String id;
  final MessageRole role;
  final String content;
  final bool isVoicePrompt;
  final DateTime timestamp;
  final VerdictStatus? verdict;
  final String? verdictLabel;
  final List<PolicyCitation> citations;
  final List<String> followUps;

  ChatMessageItem({
    required this.id,
    required this.role,
    required this.content,
    this.isVoicePrompt = false,
    DateTime? timestamp,
    this.verdict,
    this.verdictLabel,
    this.citations = const [],
    this.followUps = const [],
  }) : timestamp = timestamp ?? DateTime.now();
}

class ChatState {
  final List<ChatMessageItem> messages;
  final bool isThinking;
  final bool isListening;
  final String currentSpokenText;
  final String? activeSpeechMessageId;
  final String selectedLanguage; // 'hi-IN' or 'en-IN'
  final String? errorMessage;

  const ChatState({
    this.messages = const [],
    this.isThinking = false,
    this.isListening = false,
    this.currentSpokenText = '',
    this.activeSpeechMessageId,
    this.selectedLanguage = 'hi-IN',
    this.errorMessage,
  });

  ChatState copyWith({
    List<ChatMessageItem>? messages,
    bool? isThinking,
    bool? isListening,
    String? currentSpokenText,
    String? activeSpeechMessageId,
    bool clearActiveSpeech = false,
    String? selectedLanguage,
    String? errorMessage,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isThinking: isThinking ?? this.isThinking,
      isListening: isListening ?? this.isListening,
      currentSpokenText: currentSpokenText ?? this.currentSpokenText,
      activeSpeechMessageId: clearActiveSpeech
          ? null
          : (activeSpeechMessageId ?? this.activeSpeechMessageId),
      selectedLanguage: selectedLanguage ?? this.selectedLanguage,
      errorMessage: errorMessage,
    );
  }
}

class ChatNotifier extends StateNotifier<ChatState> {
  ChatNotifier()
      : super(ChatState(
          messages: _initialMessages,
        ));

  static final List<ChatMessageItem> _initialMessages = [
    ChatMessageItem(
      id: 'init-1',
      role: MessageRole.user,
      content: "Is my knee replacement covered? I've had this policy since 2022.",
      isVoicePrompt: true,
      timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
    ),
    ChatMessageItem(
      id: 'init-2',
      role: MessageRole.assistant,
      content:
          "Yes. Joint replacement has a 24-month waiting period, counted from your first policy inception on 12 Mar 2022. That waiting period concluded on 12 Mar 2024, so surgery after that date is fully covered, subject to your room-rent tier and sub-limits.",
      verdict: VerdictStatus.likelyCovered,
      verdictLabel: "Likely Covered • Waiting Period Complete",
      citations: const [
        PolicyCitation(
          ref: "Section 4.3(iv) • p. 17",
          title: "Specific Illness Waiting Period",
          quote:
              "“…excluded until the expiry of 24 months of continuous coverage after the date of inception of the first policy…”",
        ),
        PolicyCitation(
          ref: "Section 4.1 • p. 15",
          title: "In-patient Hospitalization Expenses",
          quote: "Room rent, boarding, and nursing charges subject to 1% of Sum Insured.",
        ),
      ],
      followUps: const [
        "Agar main private room lun to kitna milega?",
        "Does co-payment apply below age 61?",
        "Which documents are needed for cashless approval?",
      ],
      timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
    ),
  ];

  void setLanguage(String lang) {
    state = state.copyWith(selectedLanguage: lang);
  }

  /// Starts voice speech-to-text recognition
  Future<void> startListening({
    required void Function(String liveText) onLiveUpdate,
  }) async {
    state = state.copyWith(
      isListening: true,
      currentSpokenText: '',
      errorMessage: null,
    );

    try {
      final success = await SpeechHelper.startListening(
        lang: state.selectedLanguage,
        onResult: (transcript, isFinal) {
          state = state.copyWith(currentSpokenText: transcript);
          onLiveUpdate(transcript);
        },
        onError: (err) {
          state = state.copyWith(
            isListening: false,
            errorMessage: err,
          );
        },
        onDone: () {
          state = state.copyWith(isListening: false);
        },
      );

      if (!success) {
        state = state.copyWith(
          isListening: false,
          errorMessage: "Microphone listening could not be initialized.",
        );
      }
    } catch (e) {
      state = state.copyWith(
        isListening: false,
        errorMessage: e.toString(),
      );
    }
  }

  /// Stops voice speech-to-text recognition
  Future<void> stopListening() async {
    await SpeechHelper.stopListening();
    state = state.copyWith(isListening: false);
  }

  /// Toggle speech read-aloud (TTS) for an assistant message
  void toggleSpeechForMessage(ChatMessageItem msg) {
    if (state.activeSpeechMessageId == msg.id) {
      SpeakerHelper.stop();
      state = state.copyWith(clearActiveSpeech: true);
    } else {
      SpeakerHelper.stop();
      state = state.copyWith(activeSpeechMessageId: msg.id);

      final lang = state.selectedLanguage;
      SpeakerHelper.speak(
        msg.content,
        lang: lang,
        onEnd: () {
          state = state.copyWith(clearActiveSpeech: true);
        },
      );
    }
  }

  /// Toggle speech read-aloud (TTS) for an individual clause citation
  void toggleSpeechForCitation(String citationKey, String textToSpeak) {
    if (state.activeSpeechMessageId == citationKey) {
      SpeakerHelper.stop();
      state = state.copyWith(clearActiveSpeech: true);
    } else {
      SpeakerHelper.stop();
      state = state.copyWith(activeSpeechMessageId: citationKey);

      final lang = state.selectedLanguage;
      SpeakerHelper.speak(
        textToSpeak,
        lang: lang,
        onEnd: () {
          state = state.copyWith(clearActiveSpeech: true);
        },
      );
    }
  }

  /// Sends a prompt (typed or spoken) to ClaimSaathi AI
  Future<void> sendMessage(String text, {bool isVoice = false}) async {
    final query = text.trim();
    if (query.isEmpty) return;

    if (state.isListening) {
      await stopListening();
    }

    final userMsg = ChatMessageItem(
      id: 'user-${DateTime.now().millisecondsSinceEpoch}',
      role: MessageRole.user,
      content: query,
      isVoicePrompt: isVoice,
    );

    state = state.copyWith(
      messages: [...state.messages, userMsg],
      isThinking: true,
      errorMessage: null,
    );

    // AI response resolution with insurance intelligence
    await Future.delayed(const Duration(milliseconds: 650));

    final assistantMsg = _generateAiResponse(query);

    state = state.copyWith(
      messages: [...state.messages, assistantMsg],
      isThinking: false,
    );
  }

  void clearChat() {
    SpeakerHelper.stop();
    state = state.copyWith(
      messages: [],
      isThinking: false,
      isListening: false,
      clearActiveSpeech: true,
    );
  }

  ChatMessageItem _generateAiResponse(String query) {
    final q = query.toLowerCase();
    final id = 'bot-${DateTime.now().millisecondsSinceEpoch}';

    // 1. Cataract / Motiyabind
    if (q.contains('cataract') ||
        q.contains('motiyabind') ||
        q.contains('मोतियाबिंद') ||
        q.contains('eye')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "हाँ! Arogya Secure Gold पालिसी में मोतियाबिंद (Cataract) सर्जरी पूर्ण रूप से कवर्ड है। यह डे-केयर प्रक्रिया (Day Care Procedure) के अंतर्गत आती है, इसलिए इसमें 24 घंटे अस्पताल में भर्ती होना अनिवार्य नहीं है।\n\nकृपया ध्यान दें: प्रति आँख अधिकतम सीमा ₹40,000 (Sub-limit) है तथा 24 माह की विशिष्ट प्रतीक्षा अवधि (Waiting Period) लागू होती है।",
        verdict: VerdictStatus.limitApplies,
        verdictLabel: "कवर्ड • ₹40,000 प्रति आँख उप-सीमा",
        citations: const [
          PolicyCitation(
            ref: "Section 4.2 • p. 18",
            title: "Day Care & Cataract Treatment Limit",
            quote:
                "“Cataract treatment is subject to the per-eye sub-limit of ₹40,000 shown in the schedule and 24 months specific waiting period.”",
          ),
          PolicyCitation(
            ref: "Section 3.8 • p. 11",
            title: "Day Care Surgeries (No 24h requirement)",
            quote:
                "“Medical treatment and surgical procedures undertaken under general or local anesthesia in a hospital/day care centre in less than 24 hrs.”",
          ),
        ],
        followUps: const [
          "Agar dono aankhon ka operation ho to limit kya hogi?",
          "Room rent limit kitna hai?",
          "Cashless hospital me pre-auth kaise lein?",
        ],
      );
    }

    // 2. Room Rent / Private Room / Kamra
    if (q.contains('room') ||
        q.contains('private') ||
        q.contains('kamra') ||
        q.contains('कमरा') ||
        q.contains('rent') ||
        q.contains('icu')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "आपकी पालिसी में सामान्य रूम रेंट की सीमा बीमा राशि (Sum Insured ₹5,00,000) का 1% अर्थात् ₹5,000 प्रति दिन है।\n\nसावधानी: यदि आप ₹8,000 का प्राइवेट कमरा चुनते हैं, तो अतिरिक्त किराए के साथ-साथ डॉक्टर फीस, नर्सिंग और डायग्नोस्टिक बिलों पर भी 'अनुपातिक कटौती' (Proportionate Deduction) लग सकती है। सुरक्षित क्लेम हेतु ₹5,000 तक का कमरा चुनें। आईसीयू (ICU) सीमा ₹10,000/दिन (2% of SI) है।",
        verdict: VerdictStatus.limitApplies,
        verdictLabel: "सीमा लागू • 1% बीमा राशि/दिन (₹5,000)",
        citations: const [
          PolicyCitation(
            ref: "Section 4.1 • p. 15",
            title: "Room Boarding and Nursing Limitation",
            quote:
                "“Room rent, boarding and nursing expenses are limited to 1% of Sum Insured per day. ICU expenses limited to 2% of SI.”",
          ),
          PolicyCitation(
            ref: "Section 4.1.2 • p. 16",
            title: "Proportionate Deduction Clause",
            quote:
                "“If the insured occupies a room with rent higher than the entitled limit, other associate medical expenses shall be borne proportionally.”",
          ),
        ],
        followUps: const [
          "ICU me admit hone par proportionate deduction lagta hai?",
          "Kya private room upgrade cashless me allowed hai?",
        ],
      );
    }

    // 3. Knee / Joint / Ghutna / Hip replacement
    if (q.contains('knee') ||
        q.contains('joint') ||
        q.contains('replacement') ||
        q.contains('ghutna') ||
        q.contains('घुटना')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "Yes. Joint replacement (Knee/Hip surgery) is covered after 24 months of continuous coverage from the date of first policy inception.\n\nIf your policy has been continuously active for over 2 years, your surgery is eligible for 100% cashless pre-authorization, including the cost of standard approved orthopedic implants.",
        verdict: VerdictStatus.likelyCovered,
        verdictLabel: "Fully Covered • Waiting Period Satisfied",
        citations: const [
          PolicyCitation(
            ref: "Section 4.3(iv) • p. 17",
            title: "Joint Replacement Specific Waiting Period",
            quote:
                "“…excluded until the expiry of 24 months of continuous coverage after the date of inception of the first policy…”",
          ),
          PolicyCitation(
            ref: "Section 4.4 • p. 19",
            title: "Internal Prosthetic & Implant Devices",
            quote: "Costs of approved knee/hip prosthetics reimbursable up to specified SI.",
          ),
        ],
        followUps: const [
          "Which documents do I need for a cashless claim?",
          "What is the room rent limit?",
          "Is robotic knee surgery covered?",
        ],
      );
    }

    // 4. Cashless / Documents / Admission / Dastavez
    if (q.contains('cashless') ||
        q.contains('document') ||
        q.contains('dastavez') ||
        q.contains('paper') ||
        q.contains('admission') ||
        q.contains('दस्तावेज़')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "कैशलेस क्लेम (Cashless Claim) के लिए अस्पताल के TPA हेल्पडेस्क पर निम्नलिखित दस्तावेज़ प्रस्तुत करें:\n\n1. पॉलिसी हेल्थ कार्ड / पॉलिसी शिड्यूल नंबर\n2. मरीज का आधार कार्ड / सरकारी फोटो पहचान पत्र\n3. डॉक्टर की पर्ची जिसमें अस्पताल में भर्ती होने की सलाह (Admission Advice) हो\n4. बीमारी की शुरुआती जाँच रिपोर्ट (Blood tests, X-Ray, ECG आदि)\n5. टीपीए प्री-ऑथराइजेशन फॉर्म (अस्पताल द्वारा भरा हुआ)।\n\nनियोजित (Planned) इलाज के लिए 48 घंटे पूर्व तथा आपातकालीन (Emergency) स्थिति में 24 घंटे के अंदर आवेदन करें।",
        verdict: VerdictStatus.likelyCovered,
        verdictLabel: "दस्तावेज़ चेकलिस्ट तैयार",
        citations: const [
          PolicyCitation(
            ref: "Section 6.1 • p. 21",
            title: "Cashless Pre-Authorization Protocol",
            quote:
                "“Submit policy schedule, valid identification, attending physician admission advice, and test diagnostics for pre-authorization.”",
          ),
        ],
        followUps: const [
          "Agar TPA cashless deny kar de to reimbursement kaise milega?",
          "Emergency me bina card cashless ho sakta hai?",
        ],
      );
    }

    // 5. Pre-existing disease / PED / Diabetes / BP / Purani bimari
    if (q.contains('pre-existing') ||
        q.contains('ped') ||
        q.contains('diabetes') ||
        q.contains('sugar') ||
        q.contains('bp') ||
        q.contains('hypertension') ||
        q.contains('purani') ||
        q.contains('पुरानी')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "पालिसी लेते समय घोषित की गई पुरानी बीमारियों (Pre-existing Diseases जैसे Diabetes, BP) के लिए 36 महीने (3 वर्ष) की प्रतीक्षा अवधि होती है।\n\nमहत्वपूर्ण IRDAI नियम: यदि किसी असंबंधित अचानक आपातकालीन स्थिति (जैसे Acute Appendicitis, Food Poisoning, या Trauma) में भर्ती होना पड़ा हो, तो बीमा कंपनी पुरानी बीमारी का झूठा बहाना बनाकर क्लेम खारिज नहीं कर सकती।",
        verdict: VerdictStatus.waitingPeriod,
        verdictLabel: "36 माह प्रतीक्षा अवधि • आकस्मिक स्थिति में संरक्षण",
        citations: const [
          PolicyCitation(
            ref: "Section 4.1(i) • p. 16",
            title: "Pre-Existing Diseases Exclusion Clause",
            quote:
                "“Expenses related to pre-existing conditions shall be excluded until 36 months of continuous coverage after policy inception.”",
          ),
          PolicyCitation(
            ref: "IRDAI Master Circular 2024 • Clause 12",
            title: "Emergency Non-Repudiation Rule",
            quote:
                "“Emergency life-saving hospitalization cannot be denied solely on technical pre-existing non-disclosure without concrete medical history.”",
          ),
        ],
        followUps: const [
          "Bina disclosure ke agar claim reject ho to kya karein?",
          "Insurance Ombudsman me complaint kaise darj karein?",
        ],
      );
    }

    // 6. Rejection / Kharij / Dispute / Ombudsman
    if (q.contains('reject') ||
        q.contains('kharij') ||
        q.contains('खारिज') ||
        q.contains('dispute') ||
        q.contains('ombudsman') ||
        q.contains('शिकायत') ||
        q.contains('appeal')) {
      return ChatMessageItem(
        id: id,
        role: MessageRole.assistant,
        content:
            "यदि बीमा कंपनी ने आपका क्लेम अवैध रूप से खारिज किया है, तो IRDAI सुरक्षा नियमों के अंतर्गत आपके पास कानूनी अधिकार हैं:\n\n1. बीमा कंपनी के Grievance Redressal Officer (GRO) को 30-दिवसीय वैधानिक नोटिस भेजें।\n2. 30 दिन में समाधान न मिलने पर इंश्योरेंस ओम्बड्समैन (Insurance Ombudsman) के समक्ष निःशुल्क शिकायत दर्ज करें। ओम्बड्समैन ₹50,00,000 तक का हर्जाना स्वीकृत कर सकता है।\n\nआप ClaimSaathi के 'Speaker Defense' सेक्शन में जाकर अपने पक्ष की वैधानिक ऑडियो दलील भी सुन सकते हैं।",
        verdict: VerdictStatus.likelyCovered,
        verdictLabel: "IRDAI कानूनी संरक्षण • क्लेम ओवरटर्न",
        citations: const [
          PolicyCitation(
            ref: "IRDAI Grievance Redressal Rules • 2024",
            title: "Statutory 30-Day Resolution Window",
            quote:
                "“Insurers must resolve consumer grievances within 30 days failing which the policyholder can approach the Insurance Ombudsman.”",
          ),
        ],
        followUps: const [
          "Speaker Defense audio sunen",
          "Hospital bill evidence upload karein",
        ],
      );
    }

    // 7. General / Fallback
    return ChatMessageItem(
      id: id,
      role: MessageRole.assistant,
      content:
          "आपकी Arogya Secure Gold (SI ₹5,00,000) पालिसी के अनुसार, इन-पेशेंट अस्पताल भर्ती, डे-केयर सर्जरी, एम्बुलेंस शुल्क (₹2,500 तक) तथा भर्ती से 60 दिन पूर्व व 90 दिन पश्चात के खर्च कवर हैं।\n\nविशेष बीमारी या सर्जरी के लिए विशिष्ट उप-सीमा व प्रतीक्षा अवधि जांचने हेतु आप प्रश्न बोलकर या लिखकर पूछ सकते हैं।",
      verdict: VerdictStatus.likelyCovered,
      verdictLabel: "पालिसी के अनुसार कवर्ड",
      citations: const [
        PolicyCitation(
          ref: "Section 2.1 • p. 7",
          title: "Comprehensive Health Cover Schedule",
          quote:
              "“Inpatient care, Day Care procedures, Pre-hospitalization (60 days) and Post-hospitalization (90 days) eligible under active sum insured.”",
        ),
      ],
      followUps: const [
        "Kya cataract surgery ka poora paisa milega?",
        "Agar main private room lun to kitna milega?",
        "Which documents do I need for a cashless claim?",
      ],
    );
  }
}

final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  return ChatNotifier();
});
