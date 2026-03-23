import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:provider/provider.dart';

import 'package:english_trainer/presentation/pages/practice/practice_page.dart';
import 'package:english_trainer/services/practice_service.dart';
import 'package:english_trainer/viewmodels/practice_viewmodel.dart';
import 'package:english_trainer/models/practice_model.dart';
import 'package:english_trainer/models/dialogue_model.dart';
import 'package:english_trainer/core/exceptions/app_exceptions.dart';

@GenerateMocks([PracticeService])
import 'practice_page_test.mocks.dart';

void main() {
  late MockPracticeService mockPracticeService;
  late PracticeViewModel viewModel;

  setUp(() {
    mockPracticeService = MockPracticeService();
    viewModel = PracticeViewModel(mockPracticeService);
  });

  Widget createPracticeScreen() {
    return MaterialApp(
      home: ChangeNotifierProvider<PracticeViewModel>(
        create: (_) => viewModel,
        child: const PracticePage(),
      ),
    );
  }

  final mockDialogueLines = [
    DialogueLine(
      id: 1,
      speaker: 'ai',
      text: 'Hello! Welcome to our store.',
      translation: '你好！欢迎来到我们的商店。',
      audioUrl: 'https://example.com/audio1.mp3',
    ),
    DialogueLine(
      id: 2,
      speaker: 'user',
      text: 'Thank you. I am looking for a gift.',
      translation: '谢谢。我在找一份礼物。',
      audioUrl: null,
    ),
    DialogueLine(
      id: 3,
      speaker: 'ai',
      text: 'What kind of gift are you looking for?',
      translation: '您在找什么样的礼物？',
      audioUrl: 'https://example.com/audio2.mp3',
    ),
  ];

  final mockPracticeSession = PracticeSession(
    sessionId: 'session-123',
    scenarioId: 'scenario-1',
    status: 'in_progress',
    currentLineIndex: 0,
    dialogueLines: mockDialogueLines,
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );

  group('Practice Page Widget Tests', () {
    testWidgets('should display loading indicator initially',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => Future.delayed(const Duration(seconds: 1)));

      await tester.pumpWidget(createPracticeScreen());

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should display dialogue after loading',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.text('Hello! Welcome to our store.'), findsOneWidget);
      expect(find.text('你好！欢迎来到我们的商店。'), findsOneWidget);
    });

    testWidgets('should display play button for AI lines',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.play_arrow), findsOneWidget);
    });

    testWidgets('should display recording button for user lines',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.play_arrow));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.mic), findsOneWidget);
    });

    testWidgets('should show recording indicator when recording',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.play_arrow));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.mic));
      await tester.pump();

      expect(find.byIcon(Icons.stop), findsOneWidget);
    });

    testWidgets('should display score after submission',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);
      when(mockPracticeService.submitPractice(any, any))
          .thenAnswer((_) async => PracticeEvaluation(
                sessionId: 'session-123',
                overallScore: 85,
                pronunciationScore: 88,
                fluencyScore: 82,
                createdAt: DateTime.now(),
              ));

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.play_arrow));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.mic));
      await tester.pump(const Duration(milliseconds: 500));
      await tester.tap(find.byIcon(Icons.stop));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();

      expect(find.text('85'), findsOneWidget);
      expect(find.text('Pronunciation: 88'), findsOneWidget);
      expect(find.text('Fluency: 82'), findsOneWidget);
    });

    testWidgets('should show error message on submission failure',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);
      when(mockPracticeService.submitPractice(any, any))
          .thenThrow(AppException('Submission failed'));

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.play_arrow));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.mic));
      await tester.pump(const Duration(milliseconds: 500));
      await tester.tap(find.byIcon(Icons.stop));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();

      expect(find.text('Submission failed'), findsOneWidget);
    });

    testWidgets('should navigate to result page after submission',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);
      when(mockPracticeService.submitPractice(any, any))
          .thenAnswer((_) async => PracticeEvaluation(
                sessionId: 'session-123',
                overallScore: 85,
                pronunciationScore: 88,
                fluencyScore: 82,
                createdAt: DateTime.now(),
              ));

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.play_arrow));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.mic));
      await tester.pump(const Duration(milliseconds: 500));
      await tester.tap(find.byIcon(Icons.stop));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();

      expect(find.byType(PracticePage), findsNothing);
    });

    testWidgets('should display progress indicator',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('should display current line indicator',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.text('1 / 3'), findsOneWidget);
    });

    testWidgets('should show cancel button', (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.text('Cancel'), findsOneWidget);
    });

    testWidgets('should cancel session on cancel button tap',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);
      when(mockPracticeService.cancelPractice(any))
          .thenAnswer((_) async => Future.value());

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();

      expect(find.byType(PracticePage), findsNothing);
    });

    testWidgets('should display translation toggle',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.translate), findsOneWidget);
    });

    testWidgets('should toggle translation on button tap',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenAnswer((_) async => mockPracticeSession);

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.text('你好！欢迎来到我们的商店。'), findsOneWidget);

      await tester.tap(find.byIcon(Icons.translate));
      await tester.pumpAndSettle();

      expect(find.text('你好！欢迎来到我们的商店。'), findsNothing);
    });

    testWidgets('should show error message on load failure',
        (WidgetTester tester) async {
      when(mockPracticeService.startPractice(any))
          .thenThrow(AppException('Failed to load practice'));

      await tester.pumpWidget(createPracticeScreen());
      await tester.pumpAndSettle();

      expect(find.text('Failed to load practice'), findsOneWidget);
    });
  });
}
