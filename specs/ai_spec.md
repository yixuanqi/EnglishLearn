# AI Module Specification

## 1. Overview

### 1.1 AI Services Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI SERVICES LAYER                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   LLM       │    │    TTS      │    │    STT      │
│  Service    │    │  Service    │    │  Service    │
│  (OpenAI)   │    │  (Azure)    │    │  (Azure)    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │  AI Orchestrator   │
              │   (Backend)       │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │  Pronunciation     │
              │  Evaluator        │
              │  (Azure Speech)   │
              └─────────────────────┘
```

### 1.2 AI Service Responsibilities

| Service | Responsibility | Primary Provider | Fallback |
|---------|----------------|------------------|-----------|
| LLM Service | Generate dialogues, AI responses | OpenAI GPT-4 | Azure OpenAI |
| TTS Service | Convert text to speech | Azure Neural TTS | Google TTS |
| STT Service | Transcribe user speech | Azure Speech-to-Text | Google STT |
| Pronunciation Evaluator | Score pronunciation accuracy | Azure Pronunciation Assessment | Custom Model |

---

## 2. LLM Service Specification

### 2.1 Dialogue Generation

#### Prompt Template

```python
DIALOGUE_GENERATION_PROMPT = """
You are an AI language learning assistant. Generate a realistic, educational dialogue for English speaking practice.

SCENARIO CONTEXT:
- Title: {scenario_title}
- Category: {scenario_category}
- Difficulty: {difficulty}
- Context: {context}
- User Role: {user_role}
- AI Role: {ai_role}

REQUIREMENTS:
1. Generate {num_turns} dialogue turns (alternating between user and AI)
2. Keep sentences concise and natural for spoken English
3. Include relevant vocabulary for the scenario
4. Difficulty should match {difficulty} level
5. Include practical expressions and idioms
6. Make the dialogue engaging and educational

DIALOGUE STRUCTURE:
- Opening: Greeting and introduction
- Main conversation: 6-8 exchanges covering the topic
- Closing: Professional conclusion

OUTPUT FORMAT (JSON):
{
    "lines": [
        {
            "id": 1,
            "speaker": "ai",
            "text": "Good morning! Welcome to our booth at the optics exhibition.",
            "translation": "早上好！欢迎来到我们在光学展览会的展位。"
        },
        {
            "id": 2,
            "speaker": "user",
            "text": "Thank you. I'm interested in your new laser products.",
            "translation": "谢谢。我对你们的新激光产品很感兴趣。"
        }
    ],
    "key_vocabulary": [
        {
            "word": "exhibition",
            "definition": "A public display of works of art or items of interest",
            "example": "We have a booth at the optics exhibition."
        }
    ],
    "total_turns": 8,
    "estimated_duration_minutes": 5
}

Generate the dialogue now:
"""
```

#### API Call Example

```python
from app.ai.llm_client import LLMClient
from app.core.config import settings

class DialogueService:
    def __init__(self):
        self.llm_client = LLMClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    
    async def generate_dialogue(
        self,
        scenario: Scenario,
        variation: int = 1
    ) -> Dialogue:
        prompt = DIALOGUE_GENERATION_PROMPT.format(
            scenario_title=scenario.title,
            scenario_category=scenario.category,
            difficulty=scenario.difficulty,
            context=scenario.context,
            user_role=scenario.user_role,
            ai_role=scenario.ai_role,
            num_turns=8
        )
        
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7 + (variation * 0.1),
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        dialogue_data = json.loads(response)
        return Dialogue(
            scenario_id=scenario.id,
            variation=variation,
            content=dialogue_data
        )
```

### 2.2 AI Response Generation

#### Prompt Template

```python
AI_RESPONSE_PROMPT = """
You are {ai_role} in a conversation with {user_role}. Generate a natural, contextually appropriate response.

CONVERSATION CONTEXT:
- Scenario: {scenario_title}
- Previous exchanges: {conversation_history}
- Current user input: "{user_input}"

REQUIREMENTS:
1. Respond naturally as {ai_role}
2. Keep response concise (1-2 sentences for spoken dialogue)
3. Be encouraging and educational
4. If user makes mistakes, gently correct them
5. Guide the conversation forward
6. Match the {difficulty} difficulty level

OUTPUT FORMAT (JSON):
{
    "text": "That's a great question! Our new laser system offers 50% better efficiency.",
    "translation": "这是个好问题！我们的新激光系统效率提高了50%。",
    "correction": null,
    "encouragement": "Excellent question! Your pronunciation is very clear."
}

Generate the response now:
"""
```

### 2.3 Structured Output Format

#### Dialogue Response Schema

```python
class DialogueLine(BaseModel):
    id: int
    speaker: Literal["user", "ai"]
    text: str
    translation: Optional[str] = None


class VocabularyItem(BaseModel):
    word: str
    definition: str
    example: str


class DialogueResponse(BaseModel):
    lines: List[DialogueLine]
    key_vocabulary: List[VocabularyItem]
    total_turns: int
    estimated_duration_minutes: int
```

#### AI Response Schema

```python
class AIResponse(BaseModel):
    text: str
    translation: Optional[str] = None
    correction: Optional[str] = None
    encouragement: Optional[str] = None
```

### 2.4 Fallback Strategy

```python
class LLMClient:
    async def generate_with_fallback(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        providers = [
            self._call_openai,
            self._call_azure_openai,
            self._call_anthropic
        ]
        
        last_error = None
        for provider in providers:
            try:
                return await provider(prompt, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"{provider.__name__} failed: {e}")
                continue
        
        raise AIServiceError(
            service="LLM",
            message="All LLM providers failed",
            details=str(last_error)
        )
```

---

## 3. TTS Service Specification

### 3.1 Voice Configuration

#### Available Voices

| Voice ID | Gender | Accent | Language | Use Case |
|----------|--------|---------|-----------|----------|
| en-US-JennyNeural | Female | US English | General | Default |
| en-US-GuyNeural | Male | US English | General | Alternative |
| en-GB-SoniaNeural | Female | British English | Formal | Business |
| en-IN-NeerjaNeural | Female | Indian English | Technical | Technical |
| en-AU-NatashaNeural | Female | Australian | Casual | Daily Life |

#### Voice Selection Logic

```python
def select_voice(
    scenario_category: str,
    difficulty: str,
    user_preference: Optional[str] = None
) -> str:
    if user_preference:
        return user_preference
    
    voice_mapping = {
        "business": "en-GB-SoniaNeural",
        "technical": "en-IN-NeerjaNeural",
        "exhibition": "en-US-JennyNeural",
        "daily_life": "en-US-GuyNeural"
    }
    
    return voice_mapping.get(scenario_category, "en-US-JennyNeural")
```

### 3.2 TTS Generation Request

```python
class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-JennyNeural"
    rate: str = "0"  # Speaking rate (0 = normal, -10 to +10)
    pitch: str = "0"  # Pitch adjustment
    volume: str = "0"  # Volume (+0 to +100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Good morning! Welcome to our booth.",
                "voice": "en-US-JennyNeural",
                "rate": "0",
                "pitch": "0",
                "volume": "0"
            }
        }
```

### 3.3 TTS Response Format

```python
class TTSResponse(BaseModel):
    audio_url: str
    duration_seconds: float
    file_size_bytes: int
    format: str = "wav"
    sample_rate: int = 16000
```

### 3.4 Caching Strategy

```python
class TTSService:
    def __init__(self, cache_client: Redis):
        self.cache_client = cache_client
        self.cache_ttl = 7 * 24 * 3600  # 7 days
    
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        cache_key = self._generate_cache_key(request)
        
        # Check cache first
        cached = await self.cache_client.get(cache_key)
        if cached:
            return TTSResponse(**json.loads(cached))
        
        # Generate new audio
        audio_data = await self._generate_audio(request)
        audio_url = await self._upload_audio(audio_data)
        
        response = TTSResponse(
            audio_url=audio_url,
            duration_seconds=audio_data.duration,
            file_size_bytes=len(audio_data.data)
        )
        
        # Cache the result
        await self.cache_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(response.dict())
        )
        
        return response
    
    def _generate_cache_key(self, request: TTSRequest) -> str:
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        return f"tts:{request.voice}:{text_hash}"
```

---

## 4. STT Service Specification

### 4.1 Transcription Request

```python
class STTRequest(BaseModel):
    audio_data: bytes
    audio_format: str = "wav"
    language: str = "en-US"
    profanity_filter: bool = True
    enable_word_timestamps: bool = False
    enable_diarization: bool = False
```

### 4.2 Transcription Response

```python
class WordTimestamp(BaseModel):
    word: str
    start_time: float
    end_time: float
    confidence: float


class STTResponse(BaseModel):
    text: str
    confidence: float
    language_detected: str
    duration_seconds: float
    word_timestamps: Optional[List[WordTimestamp]] = None
```

### 4.3 Audio Processing

```python
class STTService:
    async def transcribe(self, request: STTRequest) -> STTResponse:
        # Validate audio
        self._validate_audio(request.audio_data)
        
        # Convert to required format
        audio = self._convert_audio(request.audio_data, request.audio_format)
        
        # Call Azure Speech Service
        result = await self._azure_client.recognize_once_async(audio)
        
        return STTResponse(
            text=result.text,
            confidence=result.confidence,
            language_detected=result.language,
            duration_seconds=result.duration.total_seconds()
        )
    
    def _validate_audio(self, audio_data: bytes):
        if len(audio_data) == 0:
            raise ValidationError("Audio data is empty")
        
        if len(audio_data) > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError("Audio file too large")
```

---

## 5. Pronunciation Evaluation Specification

### 5.1 Basic Evaluation (Free Tier)

#### Evaluation Request

```python
class BasicEvaluationRequest(BaseModel):
    audio_data: bytes
    reference_text: str
    language: str = "en-US"
```

#### Evaluation Response

```python
class BasicEvaluationResult(BaseModel):
    overall_score: float  # 0-100
    accuracy_score: float  # 0-100
    fluency_score: float  # 0-100
    completeness_score: float  # 0-100
    pronunciation_score: float  # 0-100
    transcription: str
    feedback: str
    strengths: List[str]
    improvements: List[str]
```

#### Evaluation Logic

```python
class PronunciationEvaluator:
    async def evaluate_basic(
        self,
        request: BasicEvaluationRequest
    ) -> BasicEvaluationResult:
        # Get transcription
        stt_result = await self.stt_service.transcribe(
            STTRequest(
                audio_data=request.audio_data,
                language=request.language
            )
        )
        
        # Call Azure Pronunciation Assessment
        assessment = await self._azure_client.assess_pronunciation(
            audio=request.audio_data,
            reference_text=request.reference_text,
            grading_system="HundredMark"
        )
        
        # Calculate scores
        return BasicEvaluationResult(
            overall_score=assessment.pronunciation_score,
            accuracy_score=assessment.accuracy_score,
            fluency_score=assessment.fluency_score,
            completeness_score=assessment.completeness_score,
            pronunciation_score=assessment.pronunciation_score,
            transcription=stt_result.text,
            feedback=self._generate_feedback(assessment),
            strengths=self._identify_strengths(assessment),
            improvements=self._identify_improvements(assessment)
        )
```

### 5.2 Advanced Evaluation (Premium)

#### Evaluation Request

```python
class AdvancedEvaluationRequest(BaseModel):
    audio_data: bytes
    reference_text: str
    language: str = "en-US"
    include_phonemes: bool = True
    granularity: Literal["word", "phoneme", "both"] = "both"
```

#### Evaluation Response

```python
class PhonemeEvaluation(BaseModel):
    phoneme: str
    accuracy_score: float
    error_type: Optional[Literal["none", "substitution", "insertion", "omission"]]


class WordEvaluation(BaseModel):
    word: str
    accuracy_score: float
    error_type: Optional[Literal["none", "mispronunciation", "omission", "insertion"]]
    phonemes: List[PhonemeEvaluation]


class AdvancedEvaluationResult(BaseModel):
    overall_score: float
    accuracy_score: float
    fluency_score: float
    completeness_score: float
    pronunciation_score: float
    transcription: str
    word_evaluations: List[WordEvaluation]
    feedback: str
    strengths: List[str]
    improvements: List[str]
    practice_suggestions: List[str]
```

#### Word-Level Evaluation

```python
class PronunciationEvaluator:
    async def evaluate_advanced(
        self,
        request: AdvancedEvaluationRequest
    ) -> AdvancedEvaluationResult:
        # Get detailed assessment
        assessment = await self._azure_client.assess_pronunciation(
            audio=request.audio_data,
            reference_text=request.reference_text,
            grading_system="HundredMark",
            detail_level="Word"
        )
        
        # Process word-level results
        word_evaluations = []
        for word_result in assessment.words:
            word_evaluations.append(
                WordEvaluation(
                    word=word_result.word,
                    accuracy_score=word_result.accuracy_score,
                    error_type=word_result.error_type,
                    phonemes=self._process_phonemes(word_result.phonemes)
                )
            )
        
        return AdvancedEvaluationResult(
            overall_score=assessment.pronunciation_score,
            accuracy_score=assessment.accuracy_score,
            fluency_score=assessment.fluency_score,
            completeness_score=assessment.completeness_score,
            pronunciation_score=assessment.pronunciation_score,
            transcription=assessment.transcription,
            word_evaluations=word_evaluations,
            feedback=self._generate_detailed_feedback(assessment),
            strengths=self._identify_strengths(assessment),
            improvements=self._identify_improvements(assessment),
            practice_suggestions=self._generate_practice_suggestions(assessment)
        )
```

### 5.3 Feedback Generation

```python
class FeedbackGenerator:
    def generate_feedback(self, assessment: PronunciationAssessment) -> str:
        score = assessment.pronunciation_score
        
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
    
    def identify_strengths(self, assessment: PronunciationAssessment) -> List[str]:
        strengths = []
        
        if assessment.fluency_score >= 80:
            strengths.append("Good fluency and natural rhythm")
        if assessment.accuracy_score >= 80:
            strengths.append("Accurate word pronunciation")
        if assessment.completeness_score >= 90:
            strengths.append("Complete speech without omissions")
        
        return strengths if strengths else ["Keep practicing to build your strengths"]
    
    def identify_improvements(self, assessment: PronunciationAssessment) -> List[str]:
        improvements = []
        
        if assessment.fluency_score < 70:
            improvements.append("Work on speaking more smoothly and naturally")
        if assessment.accuracy_score < 70:
            improvements.append("Focus on correct pronunciation of difficult words")
        if assessment.completeness_score < 80:
            improvements.append("Try to complete all words in the sentence")
        
        return improvements if improvements else ["Continue practicing to refine your skills"]
```

---

## 6. AI Service Error Handling

### 6.1 Error Categories

| Error Type | HTTP Status | Retry Strategy | Fallback Action |
|-------------|--------------|-----------------|-----------------|
| Rate Limiting | 429 | Exponential backoff | Switch provider |
| Timeout | 504 | Retry 3x | Use cached response |
| Invalid Input | 400 | No retry | Return validation error |
| Service Unavailable | 503 | Retry with backoff | Switch provider |
| Authentication Error | 401 | No retry | Alert admin |
| Quota Exceeded | 429 | No retry | Use fallback provider |

### 6.2 Retry Logic

```python
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    exponential_base: float = 2.0


async def retry_with_backoff(
    func: Callable,
    config: RetryConfig = RetryConfig()
):
    last_error = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func()
        except (TimeoutError, ServiceUnavailableError) as e:
            last_error = e
            if attempt == config.max_attempts - 1:
                break
            
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            await asyncio.sleep(delay)
    
    raise AIServiceError(
        service="AI",
        message=f"Max retry attempts exceeded",
        details=str(last_error)
    )
```

### 6.3 Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise AIServiceError("Circuit breaker is open")
        
        try:
            result = await func()
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e
```

---

## 7. AI Service Monitoring

### 7.1 Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| API Latency (p95) | Response time | > 5s |
| Error Rate | Failed requests | > 5% |
| Rate Limit Hits | 429 responses | > 10/min |
| Token Usage | Tokens consumed | > 90% quota |
| Cache Hit Rate | Cache effectiveness | < 50% |
| Cost per Request | API cost | > $0.01 |

### 7.2 Logging

```python
class AILogger:
    def log_request(
        self,
        service: str,
        operation: str,
        request_data: dict,
        metadata: dict = None
    ):
        logger.info(
            f"AI Service Request",
            extra={
                "service": service,
                "operation": operation,
                "request": request_data,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_response(
        self,
        service: str,
        operation: str,
        response_data: dict,
        latency_ms: float,
        success: bool
    ):
        logger.info(
            f"AI Service Response",
            extra={
                "service": service,
                "operation": operation,
                "response": response_data,
                "latency_ms": latency_ms,
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

---

## 8. Cost Optimization

### 8.1 Token Usage Tracking

```python
class TokenTracker:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def track_usage(
        self,
        service: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"tokens:{service}:{model}:{today}"
        
        await self.redis.hincrby(key, "input_tokens", input_tokens)
        await self.redis.hincrby(key, "output_tokens", output_tokens)
        await self.redis.expire(key, 30 * 24 * 3600)  # 30 days
    
    async def get_daily_usage(
        self,
        service: str,
        model: str,
        date: str
    ) -> dict:
        key = f"tokens:{service}:{model}:{date}"
        return await self.redis.hgetall(key)
```

### 8.2 Cost Estimation

```python
COST_PER_TOKEN = {
    "gpt-4": {
        "input": 0.00003,  # $0.03 per 1K tokens
        "output": 0.00006  # $0.06 per 1K tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0000015,
        "output": 0.000002
    }
}

def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    costs = COST_PER_TOKEN[model]
    input_cost = (input_tokens / 1000) * costs["input"]
    output_cost = (output_tokens / 1000) * costs["output"]
    return input_cost + output_cost
```

---

## 9. Quality Assurance

### 9.1 Response Validation

```python
class ResponseValidator:
    def validate_dialogue(self, dialogue: dict) -> bool:
        if "lines" not in dialogue:
            return False
        
        if not isinstance(dialogue["lines"], list):
            return False
        
        if len(dialogue["lines"]) < 4:
            return False
        
        for line in dialogue["lines"]:
            if not all(k in line for k in ["id", "speaker", "text"]):
                return False
            
            if line["speaker"] not in ["user", "ai"]:
                return False
        
        return True
    
    def validate_ai_response(self, response: dict) -> bool:
        required_fields = ["text"]
        return all(field in response for field in required_fields)
```

### 9.2 Content Moderation

```python
class ContentModerator:
    def __init__(self, moderation_client):
        self.moderation_client = moderation_client
    
    async def moderate_content(self, text: str) -> dict:
        result = await self.moderation_client.moderate(text)
        
        if result.flagged:
            logger.warning(f"Content flagged: {result.categories}")
            return {
                "allowed": False,
                "reason": result.categories,
                "suggestion": "Please rephrase your response."
            }
        
        return {"allowed": True}
```

---

## 10. Testing AI Services

### 10.1 Mocking AI Responses

```python
class MockLLMClient:
    async def generate(self, prompt: str, **kwargs) -> str:
        return json.dumps({
            "lines": [
                {"id": 1, "speaker": "ai", "text": "Hello!"},
                {"id": 2, "speaker": "user", "text": "Hi there!"}
            ],
            "total_turns": 2
        })


class MockTTSService:
    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        return TTSResponse(
            audio_url="https://example.com/audio/mock.wav",
            duration_seconds=5.0,
            file_size_bytes=50000
        )
```

### 10.2 Integration Testing

```python
@pytest.mark.asyncio
async def test_llm_service_integration():
    client = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.generate(
        prompt="Generate a dialogue about optics exhibition.",
        temperature=0.7
    )
    
    assert response is not None
    assert len(response) > 0
    
    dialogue = json.loads(response)
    assert "lines" in dialogue
    assert len(dialogue["lines"]) > 0
```
