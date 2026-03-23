"""Dialogue service."""

import json
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.config import ai_settings
from app.ai.llm_client import LLMClient
from app.models.dialogue import Dialogue
from app.models.scenario import Scenario
from app.schemas.dialogue import DialogueCreate, DialogueLine, DialogueResponse, SpeakerType, VocabularyItem


class DialogueService:
    """Service for dialogue operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.llm_client = LLMClient()

    async def get_dialogue(self, dialogue_id: UUID) -> Optional[Dialogue]:
        """Get dialogue by ID."""
        result = await self.db.execute(
            select(Dialogue).where(Dialogue.id == dialogue_id)
        )
        return result.scalar_one_or_none()

    async def get_dialogue_by_scenario(
        self,
        scenario_id: UUID,
        variation: int = 1,
    ) -> Optional[Dialogue]:
        """Get dialogue by scenario ID and variation."""
        result = await self.db.execute(
            select(Dialogue).where(
                Dialogue.scenario_id == scenario_id,
                Dialogue.variation == variation,
            )
        )
        return result.scalar_one_or_none()

    async def create_dialogue(self, dialogue_data: DialogueCreate) -> Dialogue:
        """Create a new dialogue."""
        dialogue = Dialogue(**dialogue_data.model_dump())
        self.db.add(dialogue)
        await self.db.commit()
        await self.db.refresh(dialogue)
        return dialogue

    async def generate_dialogue(
        self,
        scenario_id: UUID,
        variation: int = 1,
    ) -> Dialogue:
        """Generate a dialogue using AI."""
        result = await self.db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        existing = await self.get_dialogue_by_scenario(scenario_id, variation)
        if existing:
            return existing

        try:
            ai_dialogue = await self._generate_with_ai(
                scenario_title=scenario.title,
                scenario_category=scenario.category,
                difficulty=scenario.difficulty or "intermediate",
                user_role=scenario.user_role or "Learner",
                ai_role=scenario.ai_role or "Native Speaker",
                num_turns=8,
            )

            dialogue_data = DialogueCreate(
                id=uuid4(),
                scenario_id=scenario_id,
                variation=variation,
                lines=[
                    DialogueLine(
                        id=line["id"],
                        speaker=SpeakerType(line["speaker"]),
                        text=line["text"],
                        translation=line.get("translation"),
                    )
                    for line in ai_dialogue.get("lines", [])
                ],
                key_vocabulary=[
                    VocabularyItem(
                        word=vocab["word"],
                        definition=vocab["definition"],
                        example=vocab["example"],
                    )
                    for vocab in ai_dialogue.get("key_vocabulary", [])
                ],
                total_turns=ai_dialogue.get("total_turns", len(ai_dialogue.get("lines", []))),
                estimated_duration=ai_dialogue.get("estimated_duration_minutes", 5),
            )

            dialogue = await self.create_dialogue(dialogue_data)
            return dialogue

        except Exception as e:
            raise ValueError(f"Failed to generate dialogue: {str(e)}")

    async def _generate_with_ai(
        self,
        scenario_title: str,
        scenario_category: str,
        difficulty: str,
        user_role: str,
        ai_role: str,
        num_turns: int = 8,
    ) -> dict[str, Any]:
        """Generate dialogue using LLM."""
        prompt = f"""You are an AI language learning assistant. Generate a realistic, educational dialogue for English speaking practice.

SCENARIO CONTEXT:
- Title: {scenario_title}
- Category: {scenario_category}
- Difficulty: {difficulty}
- User Role: {user_role}
- AI Role: {ai_role}

REQUIREMENTS:
1. Generate {num_turns} dialogue turns (alternating between user and AI)
2. Keep sentences concise and natural for spoken English
3. Include relevant vocabulary for the scenario
4. Difficulty should match {difficulty} level
5. Include practical expressions and idioms
6. Make the dialogue engaging and educational

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
    "total_turns": {num_turns},
    "estimated_duration_minutes": 5
}}

Generate the dialogue now:"""

        system_prompt = "You are a helpful AI assistant that generates educational dialogues. Always respond with valid JSON."

        response = await self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return response
