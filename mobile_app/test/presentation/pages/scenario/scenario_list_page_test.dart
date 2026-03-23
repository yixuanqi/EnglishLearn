import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:provider/provider.dart';

import 'package:english_trainer/presentation/pages/scenario/scenario_list_page.dart';
import 'package:english_trainer/services/scenario_service.dart';
import 'package:english_trainer/viewmodels/scenario_viewmodel.dart';
import 'package:english_trainer/models/scenario_model.dart';
import 'package:english_trainer/core/exceptions/app_exceptions.dart';

@GenerateMocks([ScenarioService])
import 'scenario_list_page_test.mocks.dart';

void main() {
  late MockScenarioService mockScenarioService;
  late ScenarioViewModel viewModel;

  setUp(() {
    mockScenarioService = MockScenarioService();
    viewModel = ScenarioViewModel(mockScenarioService);
  });

  Widget createScenarioListScreen() {
    return MaterialApp(
      home: ChangeNotifierProvider<ScenarioViewModel>(
        create: (_) => viewModel,
        child: const ScenarioListPage(),
      ),
    );
  }

  final mockScenarios = [
    Scenario(
      id: '1',
      title: 'Business Meeting',
      description: 'Practice business meeting scenarios',
      category: 'business',
      difficulty: 'intermediate',
      estimatedDuration: 10,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
    Scenario(
      id: '2',
      title: 'Job Interview',
      description: 'Practice job interview scenarios',
      category: 'business',
      difficulty: 'advanced',
      estimatedDuration: 15,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ),
  ];

  group('Scenario List Page Widget Tests', () {
    testWidgets('should display loading indicator initially',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios()).thenAnswer(
        (_) async => Future.delayed(const Duration(seconds: 1)),
      );

      await tester.pumpWidget(createScenarioListScreen());

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should display scenario list after loading',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('Business Meeting'), findsOneWidget);
      expect(find.text('Job Interview'), findsOneWidget);
      expect(find.byType(Card), findsNWidgets(2));
    });

    testWidgets('should display filter chips', (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('All'), findsOneWidget);
      expect(find.text('Business'), findsOneWidget);
      expect(find.text('Exhibition'), findsOneWidget);
    });

    testWidgets('should filter scenarios by category',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Business'));
      await tester.pumpAndSettle();

      expect(find.text('Business Meeting'), findsOneWidget);
      expect(find.text('Job Interview'), findsOneWidget);
    });

    testWidgets('should filter scenarios by difficulty',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Advanced'));
      await tester.pumpAndSettle();

      expect(find.text('Job Interview'), findsOneWidget);
      expect(find.text('Business Meeting'), findsNothing);
    });

    testWidgets('should show error message on failure',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios()).thenThrow(
        AppException('Failed to load scenarios'),
      );

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('Failed to load scenarios'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });

    testWidgets('should retry on error button tap',
        (WidgetTester tester) async {
      var callCount = 0;
      when(mockScenarioService.getScenarios()).thenAnswer((_) async {
        callCount++;
        if (callCount == 1) {
          throw AppException('Failed to load scenarios');
        }
        return mockScenarios;
      });

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('Failed to load scenarios'), findsOneWidget);

      await tester.tap(find.text('Retry'));
      await tester.pumpAndSettle();

      expect(find.text('Business Meeting'), findsOneWidget);
    });

    testWidgets('should navigate to practice page on scenario tap',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Business Meeting'));
      await tester.pumpAndSettle();

      expect(find.byType(ScenarioListPage), findsNothing);
    });

    testWidgets('should display scenario details in card',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios())
          .thenAnswer((_) async => mockScenarios);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('Business Meeting'), findsOneWidget);
      expect(find.text('Practice business meeting scenarios'),
          findsOneWidget);
      expect(find.text('Intermediate'), findsOneWidget);
      expect(find.text('10 min'), findsOneWidget);
    });

    testWidgets('should display empty state when no scenarios',
        (WidgetTester tester) async {
      when(mockScenarioService.getScenarios()).thenAnswer((_) async => []);

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(find.text('No scenarios found'), findsOneWidget);
    });

    testWidgets('should refresh scenarios on pull to refresh',
        (WidgetTester tester) async {
      var callCount = 0;
      when(mockScenarioService.getScenarios()).thenAnswer((_) async {
        callCount++;
        return mockScenarios;
      });

      await tester.pumpWidget(createScenarioListScreen());
      await tester.pumpAndSettle();

      expect(callCount, equals(1));

      await tester.drag(
        find.byType(RefreshIndicator),
        const Offset(0, 300),
      );
      await tester.pumpAndSettle();

      expect(callCount, equals(2));
    });
  });
}
