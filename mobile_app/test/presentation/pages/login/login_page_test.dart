import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:provider/provider.dart';

import 'package:english_trainer/presentation/pages/login/login_page.dart';
import 'package:english_trainer/services/api_service.dart';
import 'package:english_trainer/core/services/auth_service.dart';
import 'package:english_trainer/viewmodels/login_viewmodel.dart';
import 'package:english_trainer/core/exceptions/app_exceptions.dart';

@GenerateMocks([ApiService, AuthService])
import 'login_page_test.mocks.dart';

void main() {
  late MockApiService mockApiService;
  late MockAuthService mockAuthService;
  late LoginViewModel viewModel;

  setUp(() {
    mockApiService = MockApiService();
    mockAuthService = MockAuthService();
    viewModel = LoginViewModel(mockAuthService);
  });

  Widget createLoginScreen() {
    return MaterialApp(
      home: ChangeNotifierProvider<LoginViewModel>(
        create: (_) => viewModel,
        child: const LoginPage(),
      ),
    );
  }

  group('Login Page Widget Tests', () {
    testWidgets('should display email and password fields',
        (WidgetTester tester) async {
      await tester.pumpWidget(createLoginScreen());

      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2));
    });

    testWidgets('should display login and register buttons',
        (WidgetTester tester) async {
      await tester.pumpWidget(createLoginScreen());

      expect(find.text('Login'), findsOneWidget);
      expect(find.text('Register'), findsOneWidget);
    });

    testWidgets('should show error message when login fails',
        (WidgetTester tester) async {
      when(mockAuthService.login(
        email: anyNamed('email'),
        password: anyNamed('password'),
      )).thenThrow(AppException('Invalid credentials'));

      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'test@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'password123',
      );
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle();

      expect(find.text('Invalid credentials'), findsOneWidget);
    });

    testWidgets('should navigate on successful login',
        (WidgetTester tester) async {
      when(mockAuthService.login(
        email: anyNamed('email'),
        password: anyNamed('password'),
      )).thenAnswer((_) async => Future.value());

      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'test@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'password123',
      );
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle();

      expect(find.text('Invalid credentials'), findsNothing);
    });

    testWidgets('should toggle between login and register modes',
        (WidgetTester tester) async {
      await tester.pumpWidget(createLoginScreen());

      expect(find.text('Login'), findsOneWidget);
      expect(find.text('Register'), findsOneWidget);

      await tester.tap(find.text('Register'));
      await tester.pumpAndSettle();

      expect(find.text('Name'), findsOneWidget);
    });

    testWidgets('should validate email format', (WidgetTester tester) async {
      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'invalid-email',
      );
      await tester.tap(find.text('Login'));
      await tester.pump();

      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('should validate password length', (WidgetTester tester) async {
      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'test@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        '123',
      );
      await tester.tap(find.text('Login'));
      await tester.pump();

      expect(find.text('Password must be at least 6 characters'),
          findsOneWidget);
    });

    testWidgets('should show loading indicator during login',
        (WidgetTester tester) async {
      when(mockAuthService.login(
        email: anyNamed('email'),
        password: anyNamed('password'),
      )).thenAnswer((_) async {
        await Future.delayed(const Duration(seconds: 1));
      });

      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'test@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'password123',
      );
      await tester.tap(find.text('Login'));
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should clear error message on new input',
        (WidgetTester tester) async {
      when(mockAuthService.login(
        email: anyNamed('email'),
        password: anyNamed('password'),
      )).thenThrow(AppException('Invalid credentials'));

      await tester.pumpWidget(createLoginScreen());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'test@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'wrongpassword',
      );
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle();

      expect(find.text('Invalid credentials'), findsOneWidget);

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'newpassword',
      );
      await tester.pump();

      expect(find.text('Invalid credentials'), findsNothing);
    });
  });
}
