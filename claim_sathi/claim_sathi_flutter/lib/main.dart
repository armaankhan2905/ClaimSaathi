import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'client.dart';
import 'screens/main_navigation_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeClient();
  runApp(
    const ProviderScope(
      child: ClaimSaathiApp(),
    ),
  );
}

/// Builds a theme for the given [brightness].
ThemeData _buildTheme(Brightness brightness) {
  return ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF0D47A1),
      brightness: brightness,
    ),
  );
}

class ClaimSaathiApp extends StatelessWidget {
  const ClaimSaathiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ClaimSaathi',
      debugShowCheckedModeBanner: false,
      theme: _buildTheme(Brightness.light),
      darkTheme: _buildTheme(Brightness.dark),
      themeMode: ThemeMode.system,
      home: const MainNavigationScreen(),
    );
  }
}
