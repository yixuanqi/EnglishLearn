"""Pronunciation evaluation service using Azure Speech Services."""

from typing import Any, Optional

import httpx

from app.ai.config import ai_settings
from app.ai.exceptions import PronunciationError
from app.ai.retry import CircuitBreaker, RetryConfig, retry_with_backoff
from app.ai.schemas import PhonemeEvaluation, WordEvaluation
from app.ai.services.stt import STTRequest, STTService


class BasicEvaluationResult:
    """Basic pronunciation evaluation result."""

    def __init__(
        self,
        overall_score: float,
        accuracy_score: float,
        fluency_score: float,
        completeness_score: float,
        pronunciation_score: float,
        transcription: str,
        feedback: str,
        strengths: list[str],
        improvements: list[str],
    ) -> None:
        self.overall_score = overall_score
        self.accuracy_score = accuracy_score
        self.fluency_score = fluency_score
        self.completeness_score = completeness_score
        self.pronunciation_score = pronunciation_score
        self.transcription = transcription
        self.feedback = feedback
        self.strengths = strengths
        self.improvements = improvements


class AdvancedEvaluationResult(BasicEvaluationResult):
    """Advanced pronunciation evaluation result with word-level details."""

    def __init__(
        self,
        overall_score: float,
        accuracy_score: float,
        fluency_score: float,
        completeness_score: float,
        pronunciation_score: float,
        transcription: str,
        feedback: str,
        strengths: list[str],
        improvements: list[str],
        word_evaluations: list[WordEvaluation],
        practice_suggestions: list[str],
    ) -> None:
        super().__init__(
            overall_score=overall_score,
            accuracy_score=accuracy_score,
            fluency_score=fluency_score,
            completeness_score=completeness_score,
            pronunciation_score=pronunciation_score,
            transcription=transcription,
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
        )
        self.word_evaluations = word_evaluations
        self.practice_suggestions = practice_suggestions


class PronunciationEvaluator:
    """Pronunciation evaluation service using Azure Speech Services."""

    def __init__(
        self,
        subscription_key: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        self.subscription_key = subscription_key or ai_settings.azure_speech_key
        self.region = region or ai_settings.azure_speech_region
        self.stt_service = STTService(subscription_key, region)
        self.circuit_breaker = CircuitBreaker()

    async def evaluate_basic(
        self,
        audio_data: bytes,
        reference_text: str,
        language: str = "en-US",
    ) -> BasicEvaluationResult:
        """Perform basic pronunciation evaluation."""
        self._validate_inputs(audio_data, reference_text)

        assessment = await self._call_azure_assessment(
            audio_data=audio_data,
            reference_text=reference_text,
            language=language,
            granularity="Phoneme",
        )

        return self._build_basic_result(assessment)

    async def evaluate_advanced(
        self,
        audio_data: bytes,
        reference_text: str,
        language: str = "en-US",
    ) -> AdvancedEvaluationResult:
        """Perform advanced pronunciation evaluation with word-level details."""
        self._validate_inputs(audio_data, reference_text)

        assessment = await self._call_azure_assessment(
            audio_data=audio_data,
            reference_text=reference_text,
            language=language,
            granularity="Word",
        )

        return self._build_advanced_result(assessment)

    async def _call_azure_assessment(
        self,
        audio_data: bytes,
        reference_text: str,
        language: str,
        granularity: str,
    ) -> dict[str, Any]:
        """Call Azure Pronunciation Assessment API."""
        endpoint = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

        pronunciation_params = {
            "ReferenceText": reference_text,
            "GradingSystem": "HundredMark",
            "Granularity": granularity,
            "Dimension": "Comprehensive",
        }

        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "Accept": "application/json",
            "Pronunciation-Assessment": self._encode_assessment_params(pronunciation_params),
        }

        params = {"language": language}

        async def _request() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    params=params,
                    content=audio_data,
                )

                if response.status_code == 403:
                    raise PronunciationError(
                        "Azure Pronunciation Assessment authentication failed",
                        {"status": response.status_code},
                    )

                if response.status_code == 429:
                    raise PronunciationError(
                        "Azure Pronunciation Assessment rate limit exceeded",
                        {"status": response.status_code},
                    )

                if response.status_code != 200:
                    raise PronunciationError(
                        f"Azure Pronunciation Assessment error: {response.status_code}",
                        {"response": response.text[:500]},
                    )

                return response.json()

        return await self.circuit_breaker.call(
            retry_with_backoff,
            RetryConfig(max_attempts=3),
            _request,
        )

    def _encode_assessment_params(self, params: dict) -> str:
        """Encode pronunciation assessment parameters."""
        import base64

        json_str = str(params).replace("'", '"')
        return base64.b64encode(json_str.encode()).decode()

    def _build_basic_result(self, assessment: dict) -> BasicEvaluationResult:
        """Build basic evaluation result from Azure response."""
        nbest = assessment.get("NBest", [{}])[0]
        pronunciation = nbest.get("PronunciationAssessment", {})

        overall_score = pronunciation.get("PronunciationScore", 0.0)
        accuracy_score = pronunciation.get("AccuracyScore", 0.0)
        fluency_score = pronunciation.get("FluencyScore", 0.0)
        completeness_score = pronunciation.get("CompletenessScore", 0.0)

        transcription = assessment.get("DisplayText", "")

        feedback = self._generate_feedback(overall_score)
        strengths = self._identify_strengths(pronunciation)
        improvements = self._identify_improvements(pronunciation)

        return BasicEvaluationResult(
            overall_score=overall_score,
            accuracy_score=accuracy_score,
            fluency_score=fluency_score,
            completeness_score=completeness_score,
            pronunciation_score=overall_score,
            transcription=transcription,
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
        )

    def _build_advanced_result(self, assessment: dict) -> AdvancedEvaluationResult:
        """Build advanced evaluation result from Azure response."""
        basic = self._build_basic_result(assessment)

        nbest = assessment.get("NBest", [{}])[0]
        words_data = nbest.get("Words", [])

        word_evaluations = self._process_words(words_data)
        practice_suggestions = self._generate_practice_suggestions(word_evaluations)

        return AdvancedEvaluationResult(
            overall_score=basic.overall_score,
            accuracy_score=basic.accuracy_score,
            fluency_score=basic.fluency_score,
            completeness_score=basic.completeness_score,
            pronunciation_score=basic.pronunciation_score,
            transcription=basic.transcription,
            feedback=basic.feedback,
            strengths=basic.strengths,
            improvements=basic.improvements,
            word_evaluations=word_evaluations,
            practice_suggestions=practice_suggestions,
        )

    def _process_words(self, words_data: list[dict]) -> list[WordEvaluation]:
        """Process word-level evaluation data."""
        evaluations = []

        for word_data in words_data:
            pronunciation = word_data.get("PronunciationAssessment", {})

            phonemes = []
            for phoneme_data in word_data.get("Phonemes", []):
                phoneme_assessment = phoneme_data.get("PronunciationAssessment", {})
                phonemes.append(
                    PhonemeEvaluation(
                        phoneme=phoneme_data.get("Phoneme", ""),
                        accuracy_score=phoneme_assessment.get("AccuracyScore", 0.0),
                        error_type=phoneme_assessment.get("ErrorType", "none"),
                    )
                )

            evaluations.append(
                WordEvaluation(
                    word=word_data.get("Word", ""),
                    accuracy_score=pronunciation.get("AccuracyScore", 0.0),
                    error_type=pronunciation.get("ErrorType", "none"),
                    phonemes=phonemes,
                )
            )

        return evaluations

    def _generate_feedback(self, score: float) -> str:
        """Generate feedback based on score."""
        if score >= 90:
            return "Excellent pronunciation! Your speech is very clear and natural."
        elif score >= 80:
            return "Great job! Your pronunciation is clear with minor areas for improvement."
        elif score >= 70:
            return "Good effort! Focus on clarity and intonation for better results."
        elif score >= 60:
            return "Keep practicing! Pay attention to word stress and pronunciation."
        else:
            return "Don't give up! Practice regularly and focus on individual sounds."

    def _identify_strengths(self, pronunciation: dict) -> list[str]:
        """Identify pronunciation strengths."""
        strengths = []

        if pronunciation.get("FluencyScore", 0) >= 80:
            strengths.append("Good fluency and natural rhythm")
        if pronunciation.get("AccuracyScore", 0) >= 80:
            strengths.append("Accurate word pronunciation")
        if pronunciation.get("CompletenessScore", 0) >= 90:
            strengths.append("Complete speech without omissions")

        return strengths if strengths else ["Keep practicing to build your strengths"]

    def _identify_improvements(self, pronunciation: dict) -> list[str]:
        """Identify areas for improvement."""
        improvements = []

        if pronunciation.get("FluencyScore", 0) < 70:
            improvements.append("Work on speaking more smoothly and naturally")
        if pronunciation.get("AccuracyScore", 0) < 70:
            improvements.append("Focus on correct pronunciation of difficult words")
        if pronunciation.get("CompletenessScore", 0) < 80:
            improvements.append("Try to complete all words in the sentence")

        return improvements if improvements else ["Continue practicing to refine your skills"]

    def _generate_practice_suggestions(
        self,
        word_evaluations: list[WordEvaluation],
    ) -> list[str]:
        """Generate specific practice suggestions based on word evaluations."""
        suggestions = []

        problem_words = [w for w in word_evaluations if w.accuracy_score < 70]

        if problem_words:
            words_str = ", ".join([f"'{w.word}'" for w in problem_words[:3]])
            suggestions.append(f"Practice pronouncing: {words_str}")

        if len(problem_words) > 3:
            suggestions.append("Focus on difficult consonant clusters and vowel sounds")

        suggestions.append("Try shadowing exercises with native speaker audio")
        suggestions.append("Record yourself and compare with reference audio")

        return suggestions[:4]

    def _validate_inputs(self, audio_data: bytes, reference_text: str) -> None:
        """Validate evaluation inputs."""
        if not audio_data:
            raise PronunciationError("Audio data is empty")

        if not reference_text or not reference_text.strip():
            raise PronunciationError("Reference text is empty")

        if len(audio_data) > ai_settings.stt_max_audio_size:
            raise PronunciationError(
                "Audio file too large",
                {"max_size": ai_settings.stt_max_audio_size},
            )
