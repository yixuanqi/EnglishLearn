"""sqlite_compatible

Revision ID: 5f9f5f4997b7
Revises: 001_initial
Create Date: 2026-03-17 10:31:29.322711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision: str = '5f9f5f4997b7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.Text, nullable=True),
        sa.Column('english_level', sa.String(20), nullable=False, server_default='intermediate'),
        sa.Column('subscription_plan', sa.String(30), nullable=False, server_default='free'),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("english_level IN ('beginner', 'intermediate', 'advanced')", name='chk_english_level'),
        sa.CheckConstraint("subscription_plan IN ('free', 'premium_monthly', 'premium_annual')", name='chk_subscription_plan'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_subscription_plan', 'users', ['subscription_plan'])
    op.create_index('idx_users_stripe_customer_id', 'users', ['stripe_customer_id'])

    op.create_table(
        'scenarios',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='intermediate'),
        sa.Column('context', sa.Text, nullable=False),
        sa.Column('user_role', sa.String(200), nullable=False),
        sa.Column('ai_role', sa.String(200), nullable=False),
        sa.Column('key_vocabulary', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('tips', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('estimated_duration', sa.Integer, nullable=False, server_default='10'),
        sa.Column('is_premium', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('thumbnail_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("category IN ('exhibition', 'technical', 'business', 'daily_life')", name='chk_category'),
        sa.CheckConstraint("difficulty IN ('beginner', 'intermediate', 'advanced')", name='chk_difficulty'),
    )
    op.create_index('idx_scenarios_category', 'scenarios', ['category'])
    op.create_index('idx_scenarios_difficulty', 'scenarios', ['difficulty'])
    op.create_index('idx_scenarios_is_premium', 'scenarios', ['is_premium'])
    op.create_index('idx_scenarios_is_active', 'scenarios', ['is_active'])

    op.create_table(
        'dialogues',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('scenario_id', sa.String(36), sa.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('variation', sa.Integer, nullable=False, server_default='1'),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('generated_by', sa.String(50), nullable=False, server_default='openai'),
        sa.Column('generation_params', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('variation >= 1 AND variation <= 10', name='chk_variation'),
        sa.UniqueConstraint('scenario_id', 'variation', name='uq_dialogues_scenario_variation'),
    )
    op.create_index('idx_dialogues_scenario_id', 'dialogues', ['scenario_id'])

    op.create_table(
        'practice_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dialogue_id', sa.String(36), sa.ForeignKey('dialogues.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('current_turn', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_turns', sa.Integer, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('average_accuracy', sa.Numeric(5, 2), nullable=True),
        sa.Column('average_fluency', sa.Numeric(5, 2), nullable=True),
        sa.Column('average_completeness', sa.Numeric(5, 2), nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned')", name='chk_session_status'),
        sa.CheckConstraint('current_turn >= 0', name='chk_current_turn'),
    )
    op.create_index('idx_practice_sessions_user_id', 'practice_sessions', ['user_id'])
    op.create_index('idx_practice_sessions_status', 'practice_sessions', ['status'])
    op.create_index('idx_practice_sessions_started_at', 'practice_sessions', ['started_at'])
    op.create_index('idx_practice_sessions_user_started', 'practice_sessions', ['user_id', sa.text('started_at DESC')])

    op.create_table(
        'speech_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('practice_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('turn_index', sa.Integer, nullable=False),
        sa.Column('expected_text', sa.Text, nullable=False),
        sa.Column('transcription', sa.Text, nullable=True),
        sa.Column('pronunciation_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('accuracy_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('fluency_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('completeness_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('word_evaluations', sa.JSON, nullable=True),
        sa.Column('audio_url', sa.Text, nullable=True),
        sa.Column('audio_duration_seconds', sa.Numeric(5, 2), nullable=True),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('ai_response_text', sa.Text, nullable=True),
        sa.Column('ai_response_audio_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_speech_results_session_id', 'speech_results', ['session_id'])
    op.create_index('idx_speech_results_session_turn', 'speech_results', ['session_id', 'turn_index'])

    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending'),
        sa.Column('plan_type', sa.String(30), nullable=False),
        sa.Column('billing_period', sa.String(20), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('metadata', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'succeeded', 'failed', 'refunded', 'cancelled')", name='chk_payment_status'),
        sa.CheckConstraint("plan_type IN ('premium_monthly', 'premium_annual')", name='chk_plan_type'),
        sa.CheckConstraint("billing_period IN ('monthly', 'annual') OR billing_period IS NULL", name='chk_billing_period'),
    )
    op.create_index('idx_payments_user_id', 'payments', ['user_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_stripe_payment_intent', 'payments', ['stripe_payment_intent_id'])
    op.create_index('idx_payments_stripe_subscription', 'payments', ['stripe_subscription_id'])
    op.create_index('idx_payments_created_at', 'payments', ['created_at'])

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('token_hash', name='uq_refresh_tokens_token_hash'),
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])

    op.create_table(
        'custom_scenarios',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('context', sa.Text, nullable=False),
        sa.Column('user_role', sa.String(200), nullable=False),
        sa.Column('ai_role', sa.String(200), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='intermediate'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("category IN ('exhibition', 'technical', 'business', 'daily_life')", name='chk_custom_category'),
        sa.CheckConstraint("difficulty IN ('beginner', 'intermediate', 'advanced')", name='chk_custom_difficulty'),
    )
    op.create_index('idx_custom_scenarios_user_id', 'custom_scenarios', ['user_id'])


def downgrade() -> None:
    op.drop_table('custom_scenarios')
    op.drop_table('refresh_tokens')
    op.drop_table('payments')
    op.drop_table('speech_results')
    op.drop_table('practice_sessions')
    op.drop_table('dialogues')
    op.drop_table('scenarios')
    op.drop_table('users')
