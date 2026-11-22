import 'package:flutter_test/flutter_test.dart';
import 'package:claim_sathi/providers/chat_provider.dart';

void main() {
  group('ChatNotifier and Policy Intelligence Tests', () {
    test('initializes with default welcome policy insight messages', () {
      final notifier = ChatNotifier();
      expect(notifier.state.messages.length, greaterThanOrEqualTo(2));
      expect(notifier.state.messages.first.role, equals(MessageRole.user));
      expect(notifier.state.messages.last.role, equals(MessageRole.assistant));
      expect(notifier.state.messages.last.citations.isNotEmpty, isTrue);
    });

    test('sendMessage adds user prompt and generates policy intelligence response', () async {
      final notifier = ChatNotifier();
      final initialCount = notifier.state.messages.length;

      await notifier.sendMessage('Kya cataract surgery covered hai?', isVoice: true);

      expect(notifier.state.messages.length, equals(initialCount + 2));
      final userMsg = notifier.state.messages[initialCount];
      final botMsg = notifier.state.messages[initialCount + 1];

      expect(userMsg.role, equals(MessageRole.user));
      expect(userMsg.content, equals('Kya cataract surgery covered hai?'));
      expect(userMsg.isVoicePrompt, isTrue);

      expect(botMsg.role, equals(MessageRole.assistant));
      expect(botMsg.verdict, equals(VerdictStatus.limitApplies));
      expect(botMsg.citations.isNotEmpty, isTrue);
      expect(botMsg.citations.first.ref, contains('Section 4.2'));
    });

    test('switching language updates state', () {
      final notifier = ChatNotifier();
      expect(notifier.state.selectedLanguage, equals('hi-IN'));

      notifier.setLanguage('en-IN');
      expect(notifier.state.selectedLanguage, equals('en-IN'));
    });

    test('clearChat resets conversation', () {
      final notifier = ChatNotifier();
      expect(notifier.state.messages.isNotEmpty, isTrue);

      notifier.clearChat();
      expect(notifier.state.messages.isEmpty, isTrue);
    });
  });
}
