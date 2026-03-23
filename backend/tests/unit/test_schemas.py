"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from uuid import uuid4

from app.schemas.user import (
    UserRegistrationRequest,
    LoginRequest,
    RefreshTokenRequest,
    UpdateProfileRequest,
    UserProfile,
    TokenResponse,
    AuthResponse,
    SubscriptionPlan,
    EnglishLevel,
)
from app.schemas.scenario import (
    ScenarioCategory,
    DifficultyLevel,
    VocabularyItem,
    ScenarioSummary,
    ScenarioDetail,
    CreateScenarioRequest,
)
from app.schemas.practice import (
    SessionStatus,
    StartSessionRequest,
    SubmitPracticeRequest,
    SpeechResult,
    AIResponse,
)
from app.schemas.evaluation import (
    ErrorType,
    PhonemeEvaluation,
    WordEvaluation,
    BasicEvaluationResult,
    AdvancedEvaluationResult,
)


class TestUserSchemas:
    """Tests for user schemas."""

    def test_user_registration_request_valid(self):
        """Test valid user registration request."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "name": "Test User",
        }
        request = UserRegistrationRequest(**data)
        assert request.email == "test@example.com"
        assert request.name == "Test User"

    def test_user_registration_request_invalid_email(self):
        """Test user registration with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "TestPass123!",
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_short_password(self):
        """Test user registration with short password."""
        data = {
            "email": "test@example.com",
            "password": "Short1!",
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_no_uppercase(self):
        """Test user registration with no uppercase in password."""
        data = {
            "email": "test@example.com",
            "password": "testpass123!",
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_no_lowercase(self):
        """Test user registration with no lowercase in password."""
        data = {
            "email": "test@example.com",
            "password": "TESTPASS123!",
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_no_digit(self):
        """Test user registration with no digit in password."""
        data = {
            "email": "test@example.com",
            "password": "TestPassword!",
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_empty_name(self):
        """Test user registration with empty name."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "name": "",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_login_request_valid(self):
        """Test valid login request."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
        }
        request = LoginRequest(**data)
        assert request.email == "test@example.com"

    def test_login_request_invalid_email(self):
        """Test login request with invalid email."""
        data = {
            "email": "invalid",
            "password": "TestPass123!",
        }
        with pytest.raises(ValidationError):
            LoginRequest(**data)

    def test_refresh_token_request_valid(self):
        """Test valid refresh token request."""
        data = {"refresh_token": "some_token_value"}
        request = RefreshTokenRequest(**data)
        assert request.refresh_token == "some_token_value"

    def test_refresh_token_request_empty(self):
        """Test refresh token request with empty token."""
        data = {"refresh_token": ""}
        request = RefreshTokenRequest(**data)
        assert request.refresh_token == ""

    def test_update_profile_request_partial(self):
        """Test update profile request with partial data."""
        data = {"name": "New Name"}
        request = UpdateProfileRequest(**data)
        assert request.name == "New Name"
        assert request.avatar_url is None

    def test_update_profile_request_empty(self):
        """Test update profile request with empty data."""
        request = UpdateProfileRequest()
        assert request.name is None
        assert request.avatar_url is None

    def test_subscription_plan_enum(self):
        """Test subscription plan enum values."""
        assert SubscriptionPlan.FREE == "free"
        assert SubscriptionPlan.PREMIUM_MONTHLY == "premium_monthly"
        assert SubscriptionPlan.PREMIUM_ANNUAL == "premium_annual"

    def test_english_level_enum(self):
        """Test English level enum values."""
        assert EnglishLevel.BEGINNER == "beginner"
        assert EnglishLevel.INTERMEDIATE == "intermediate"
        assert EnglishLevel.ADVANCED == "advanced"


class TestScenarioSchemas:
    """Tests for scenario schemas."""

    def test_scenario_category_enum(self):
        """Test scenario category enum values."""
        assert ScenarioCategory.EXHIBITION == "exhibition"
        assert ScenarioCategory.TECHNICAL == "technical"
        assert ScenarioCategory.BUSINESS == "business"
        assert ScenarioCategory.DAILY_LIFE == "daily_life"

    def test_difficulty_level_enum(self):
        """Test difficulty level enum values."""
        assert DifficultyLevel.BEGINNER == "beginner"
        assert DifficultyLevel.INTERMEDIATE == "intermediate"
        assert DifficultyLevel.ADVANCED == "advanced"

    def test_vocabulary_item_valid(self):
        """Test valid vocabulary item."""
        data = {
            "word": "exhibition",
            "definition": "a public display of works",
            "example": "The exhibition opens tomorrow.",
        }
        item = VocabularyItem(**data)
        assert item.word == "exhibition"
        assert item.definition == "a public display of works"

    def test_vocabulary_item_missing_field(self):
        """Test vocabulary item with missing field."""
        data = {
            "word": "exhibition",
            "definition": "a public display of works",
        }
        with pytest.raises(ValidationError):
            VocabularyItem(**data)

    def test_scenario_summary_valid(self):
        """Test valid scenario summary."""
        data = {
            "id": str(uuid4()),
            "title": "Test Scenario",
            "description": "Test description",
            "category": ScenarioCategory.EXHIBITION,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "estimated_duration": 15,
            "is_premium": False,
        }
        summary = ScenarioSummary(**data)
        assert summary.title == "Test Scenario"

    def test_scenario_detail_valid(self):
        """Test valid scenario detail."""
        data = {
            "id": str(uuid4()),
            "title": "Test Scenario",
            "description": "Test description",
            "category": ScenarioCategory.EXHIBITION,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "estimated_duration": 15,
            "is_premium": False,
            "context": "Test context",
            "user_role": "Sales",
            "ai_role": "Customer",
            "key_vocabulary": [],
            "tips": [],
        }
        detail = ScenarioDetail(**data)
        assert detail.context == "Test context"

    def test_create_scenario_request_valid(self):
        """Test valid create scenario request."""
        data = {
            "title": "Test Scenario",
            "category": ScenarioCategory.EXHIBITION,
            "context": "Test context",
            "user_role": "Sales",
            "ai_role": "Customer",
        }
        request = CreateScenarioRequest(**data)
        assert request.title == "Test Scenario"
        assert request.difficulty == DifficultyLevel.INTERMEDIATE

    def test_create_scenario_request_title_too_long(self):
        """Test create scenario request with title too long."""
        data = {
            "title": "x" * 201,
            "category": ScenarioCategory.EXHIBITION,
            "context": "Test context",
            "user_role": "Sales",
            "ai_role": "Customer",
        }
        with pytest.raises(ValidationError):
            CreateScenarioRequest(**data)


class TestPracticeSchemas:
    """Tests for practice schemas."""

    def test_session_status_enum(self):
        """Test session status enum values."""
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.ABANDONED == "abandoned"

    def test_start_session_request_valid(self):
        """Test valid start session request."""
        dialogue_id = uuid4()
        data = {"dialogue_id": dialogue_id}
        request = StartSessionRequest(**data)
        assert request.dialogue_id == dialogue_id

    def test_start_session_request_invalid_uuid(self):
        """Test start session request with invalid UUID."""
        data = {"dialogue_id": "invalid-uuid"}
        with pytest.raises(ValidationError):
            StartSessionRequest(**data)

    def test_submit_practice_request_valid(self):
        """Test valid submit practice request."""
        data = {
            "session_id": str(uuid4()),
            "transcription": "Hello, how are you?",
            "pronunciation_score": 85.5,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
        }
        request = SubmitPracticeRequest(**data)
        assert request.transcription == "Hello, how are you?"

    def test_submit_practice_request_score_out_of_range(self):
        """Test submit practice request with score out of range."""
        data = {
            "session_id": str(uuid4()),
            "transcription": "Hello",
            "pronunciation_score": 150.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
        }
        with pytest.raises(ValidationError):
            SubmitPracticeRequest(**data)

    def test_submit_practice_request_negative_score(self):
        """Test submit practice request with negative score."""
        data = {
            "session_id": str(uuid4()),
            "transcription": "Hello",
            "pronunciation_score": -10.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
        }
        with pytest.raises(ValidationError):
            SubmitPracticeRequest(**data)

    def test_ai_response_valid(self):
        """Test valid AI response."""
        data = {
            "text": "I'm doing well, thank you!",
            "audio_url": "https://example.com/audio.mp3",
        }
        response = AIResponse(**data)
        assert response.text == "I'm doing well, thank you!"

    def test_ai_response_optional_audio(self):
        """Test AI response with optional audio URL."""
        data = {"text": "I'm doing well, thank you!"}
        response = AIResponse(**data)
        assert response.audio_url is None

    def test_speech_result_valid(self):
        """Test valid speech result."""
        data = {
            "transcription": "Hello",
            "expected_text": "Hello",
            "pronunciation_score": 85.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
        }
        result = SpeechResult(**data)
        assert result.transcription == "Hello"


class TestEvaluationSchemas:
    """Tests for evaluation schemas."""

    def test_error_type_enum(self):
        """Test error type enum values."""
        assert ErrorType.NONE == "none"
        assert ErrorType.MISPRONUNCIATION == "mispronunciation"
        assert ErrorType.OMISSION == "omission"
        assert ErrorType.INSERTION == "insertion"

    def test_phoneme_evaluation_valid(self):
        """Test valid phoneme evaluation."""
        data = {
            "phoneme": "AH",
            "accuracy_score": 85.0,
        }
        evaluation = PhonemeEvaluation(**data)
        assert evaluation.phoneme == "AH"
        assert evaluation.accuracy_score == 85.0

    def test_phoneme_evaluation_score_out_of_range(self):
        """Test phoneme evaluation with score out of range."""
        data = {
            "phoneme": "AH",
            "accuracy_score": 150.0,
        }
        with pytest.raises(ValidationError):
            PhonemeEvaluation(**data)

    def test_word_evaluation_valid(self):
        """Test valid word evaluation."""
        data = {
            "word": "hello",
            "accuracy_score": 90.0,
            "error_type": ErrorType.NONE,
            "phonemes": [
                {"phoneme": "HH", "accuracy_score": 95.0},
                {"phoneme": "AH", "accuracy_score": 88.0},
            ],
        }
        evaluation = WordEvaluation(**data)
        assert evaluation.word == "hello"
        assert len(evaluation.phonemes) == 2

    def test_word_evaluation_optional_error_type(self):
        """Test word evaluation with optional error type."""
        data = {
            "word": "hello",
            "accuracy_score": 90.0,
        }
        evaluation = WordEvaluation(**data)
        assert evaluation.error_type is None

    def test_basic_evaluation_result_valid(self):
        """Test valid basic evaluation result."""
        data = {
            "transcription": "Hello, how are you?",
            "overall_score": 85.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
        }
        result = BasicEvaluationResult(**data)
        assert result.transcription == "Hello, how are you?"

    def test_basic_evaluation_result_with_feedback(self):
        """Test basic evaluation result with feedback."""
        data = {
            "transcription": "Hello",
            "overall_score": 85.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
            "feedback": "Good pronunciation!",
        }
        result = BasicEvaluationResult(**data)
        assert result.feedback == "Good pronunciation!"

    def test_advanced_evaluation_result_valid(self):
        """Test valid advanced evaluation result."""
        data = {
            "transcription": "Hello",
            "overall_score": 85.0,
            "accuracy_score": 90.0,
            "fluency_score": 80.0,
            "completeness_score": 88.0,
            "word_evaluations": [
                {
                    "word": "hello",
                    "accuracy_score": 90.0,
                }
            ],
        }
        result = AdvancedEvaluationResult(**data)
        assert len(result.word_evaluations) == 1


class TestSchemaEdgeCases:
    """Edge case tests for schemas."""

    def test_user_registration_max_name_length(self):
        """Test user registration with max name length."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "name": "x" * 100,
        }
        request = UserRegistrationRequest(**data)
        assert len(request.name) == 100

    def test_user_registration_name_too_long(self):
        """Test user registration with name too long."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "name": "x" * 101,
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_password_max_length(self):
        """Test password with max length."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!" + "x" * 116,
            "name": "Test User",
        }
        request = UserRegistrationRequest(**data)
        assert len(request.password) == 128

    def test_password_too_long(self):
        """Test password too long."""
        data = {
            "email": "test@example.com",
            "password": "TestPass123!" + "x" * 117,
            "name": "Test User",
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_scenario_estimated_duration_default(self):
        """Test scenario estimated duration default value."""
        data = {
            "title": "Test",
            "category": ScenarioCategory.EXHIBITION,
            "context": "Test context",
            "user_role": "Sales",
            "ai_role": "Customer",
        }
        request = CreateScenarioRequest(**data)
        assert request.estimated_duration == 15

    def test_score_boundary_values(self):
        """Test score boundary values (0 and 100)."""
        data = {
            "session_id": str(uuid4()),
            "transcription": "Hello",
            "pronunciation_score": 0.0,
            "accuracy_score": 100.0,
            "fluency_score": 0.0,
            "completeness_score": 100.0,
        }
        request = SubmitPracticeRequest(**data)
        assert request.pronunciation_score == 0.0
        assert request.accuracy_score == 100.0
