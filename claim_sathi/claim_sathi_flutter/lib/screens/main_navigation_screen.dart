import 'package:flutter/material.dart';
import 'chat_screen.dart';
import 'defense_screen.dart';
import 'evidence_screen.dart';
import 'voice_screen.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    ChatScreen(),
    EvidenceScreen(),
    VoiceScreen(),
    DefenseScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum, color: Colors.deepPurpleAccent),
            label: 'Policy Chat',
          ),
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt, color: Colors.blueAccent),
            label: 'Camera Evidence',
          ),
          NavigationDestination(
            icon: Icon(Icons.record_voice_over_outlined),
            selectedIcon: Icon(Icons.record_voice_over, color: Colors.deepPurpleAccent),
            label: 'Voice Vault',
          ),
          NavigationDestination(
            icon: Icon(Icons.volume_up_outlined),
            selectedIcon: Icon(Icons.volume_up, color: Colors.teal),
            label: 'Speaker Defense',
          ),
        ],
      ),
    );
  }
}
