"""Dialogue generation service using LLM."""

import json
from typing import Any, Optional

from app.ai.config import ai_settings
from app.ai.exceptions import LLMServiceError
from app.ai.llm_client import AzureOpenAIClient, LLMClient
from app.ai.schemas import AIResponseContent, DialogueContent


DIALOGUE_GENERATION_PROMPT = """You are an AI language learning assistant. Generate a realistic, educational dialogue for English speaking practice.

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
{{
    "lines": [
        {{
            "id": 1,
            "speaker": "ai",
            "text": "Good morning! Welcome to our booth at the optics exhibition.",
            "translation": "早上好！欢迎来到我们在光学展览会的展位。"
        }},
        {{
            "id": 2,
            "speaker": "user",
            "text": "Thank you. I'm interested in your new laser products.",
            "translation": "谢谢。我对你们的新激光产品很感兴趣。"
        }}
    ],
    "key_vocabulary": [
        {{
            "word": "exhibition",
            "definition": "A public display of works of art or items of interest",
            "example": "We have a booth at the optics exhibition."
        }}
    ],
    "total_turns": 8,
    "estimated_duration_minutes": 5
}}

Generate the dialogue now:"""


AI_RESPONSE_PROMPT = """You are {ai_role} in a conversation with {user_role}. Generate a natural, contextually appropriate response.

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
{{
    "text": "That's a great question! Our new laser system offers 50% better efficiency.",
    "translation": "这是个好问题！我们的新激光系统效率提高了50%。",
    "correction": null,
    "encouragement": "Excellent question! Your pronunciation is very clear."
}}

Generate the response now:"""


LEARNING_FEEDBACK_PROMPT = """You are an English learning coach. Generate personalized feedback and improvement suggestions based on the practice session.

PRACTICE SESSION SUMMARY:
- Scenario: {scenario_title}
- Difficulty: {difficulty}
- Total turns: {total_turns}
- Overall score: {overall_score}
- Accuracy score: {accuracy_score}
- Fluency score: {fluency_score}
- Completeness score: {completeness_score}

WORD-LEVEL ISSUES:
{word_issues}

REQUIREMENTS:
1. Provide encouraging overall feedback
2. Identify 2-3 specific strengths
3. Identify 2-3 areas for improvement
4. Suggest specific practice exercises
5. Match the tone to the score level

OUTPUT FORMAT (JSON):
{{
    "overall_feedback": "Great practice session! You're making excellent progress.",
    "strengths": [
        "Good pronunciation of technical vocabulary",
        "Natural sentence rhythm"
    ],
    "areas_for_improvement": [
        "Work on stress patterns in longer words",
        "Practice linking words for smoother speech"
    ],
    "practice_suggestions": [
        "Practice saying 'exhibition' and 'demonstration' with correct stress",
        "Try shadowing exercises with native speaker audio"
    ],
    "next_steps": "Try a more advanced scenario to challenge yourself further."
}}

Generate the feedback now:"""


class DialogueService:
    """Service for generating dialogues and AI responses."""

    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.azure_client = AzureOpenAIClient()

    async def generate_dialogue(
        self,
        scenario_title: str,
        scenario_category: str,
        difficulty: str,
        context: str,
        user_role: str,
        ai_role: str,
        variation: int = 1,
        num_turns: int = 8,
    ) -> DialogueContent:
        """Generate a dialogue for a scenario."""
        prompt = DIALOGUE_GENERATION_PROMPT.format(
            scenario_title=scenario_title,
            scenario_category=scenario_category,
            difficulty=difficulty,
            context=context,
            user_role=user_role,
            ai_role=ai_role,
            num_turns=num_turns,
        )

        temperature = 0.7 + (variation * 0.1)
        if temperature > 1.0:
            temperature = 1.0

        try:
            response = await self.llm_client.generate_json(
                prompt=prompt,
                temperature=temperature,
                max_tokens=2000,
            )
            return DialogueContent(**response)
        except Exception as e:
            return await self._fallback_generate_dialogue(
                prompt=prompt,
                temperature=temperature,
                error=e,
            )

    async def _fallback_generate_dialogue(
        self,
        prompt: str,
        temperature: float,
        error: Exception,
    ) -> DialogueContent:
        """Fallback to Azure OpenAI if primary fails."""
        try:
            response = await self.azure_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=2000,
            )
            return DialogueContent(**json.loads(response))
        except Exception as fallback_error:
            raise LLMServiceError(
                "Failed to generate dialogue with all providers",
                {
                    "primary_error": str(error),
                    "fallback_error": str(fallback_error),
                },
            )

    async def generate_ai_response(
        self,
        scenario_title: str,
        ai_role: str,
        user_role: str,
        difficulty: str,
        conversation_history: list[dict[str, str]],
        user_input: str,
    ) -> AIResponseContent:
        """Generate AI response for user input in dialogue."""
        history_text = self._format_conversation_history(conversation_history)

        prompt = AI_RESPONSE_PROMPT.format(
            ai_role=ai_role,
            user_role=user_role,
            scenario_title=scenario_title,
            conversation_history=history_text,
            user_input=user_input,
            difficulty=difficulty,
        )

        try:
            response = await self.llm_client.generate_json(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
            )
            return AIResponseContent(**response)
        except Exception as e:
            raise LLMServiceError(
                "Failed to generate AI response",
                {"error": str(e)},
            )

    async def generate_learning_feedback(
        self,
        scenario_title: str,
        difficulty: str,
        total_turns: int,
        overall_score: float,
        accuracy_score: float,
        fluency_score: float,
        completeness_score: float,
        word_issues: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Generate personalized learning feedback."""
        issues_text = self._format_word_issues(word_issues or [])

        prompt = LEARNING_FEEDBACK_PROMPT.format(
            scenario_title=scenario_title,
            difficulty=difficulty,
            total_turns=total_turns,
            overall_score=overall_score,
            accuracy_score=accuracy_score,
            fluency_score=fluency_score,
            completeness_score=completeness_score,
            word_issues=issues_text,
        )

        try:
            response = await self.llm_client.generate_json(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000,
            )
            return response
        except Exception as e:
            raise LLMServiceError(
                "Failed to generate learning feedback",
                {"error": str(e)},
            )

    def _format_conversation_history(
        self,
        history: list[dict[str, str]],
    ) -> str:
        """Format conversation history for prompt."""
        lines = []
        for entry in history[-6:]:
            speaker = entry.get("speaker", "unknown")
            text = entry.get("text", "")
            lines.append(f"{speaker.capitalize()}: {text}")
        return "\n".join(lines)

    def _format_word_issues(
        self,
        word_issues: list[dict[str, Any]],
    ) -> str:
        """Format word issues for feedback prompt."""
        if not word_issues:
            return "No significant word-level issues detected."

        lines = []
        for issue in word_issues[:10]:
            word = issue.get("word", "")
            score = issue.get("accuracy_score", 0)
            error_type = issue.get("error_type", "none")
            if score < 80 or error_type != "none":
                lines.append(f"- '{word}': score {score:.1f}, issue: {error_type}")

        return "\n".join(lines) if lines else "No significant word-level issues detected."
