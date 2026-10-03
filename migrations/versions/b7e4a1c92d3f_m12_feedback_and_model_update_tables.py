"""M12 feedback and model update tables

Revision ID: b7e4a1c92d3f
Revises: f5c99add306d
Create Date: 2026-10-01 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7e4a1c92d3f'
down_revision: Union[str, Sequence[str], None] = 'f5c99add306d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add M12 feedback and model update tables."""
    op.create_table(
        'packaging_feedback_record',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('recommendation_run_id', sa.String(), nullable=True),
        sa.Column('candidate_id', sa.String(), nullable=True),
        sa.Column('material_id', sa.String(), nullable=True),
        sa.Column('trial_identifier', sa.String(), nullable=False),
        sa.Column('observation_origin', sa.Enum('REAL_PRODUCTION', 'REAL_PILOT', 'SYNTHETIC_TEST', 'DEMO', name='observationorigin'), nullable=False),
        sa.Column('observation_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('package_configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('observed_shelf_life_days', sa.Float(), nullable=True),
        sa.Column('observed_otr', sa.Float(), nullable=True),
        sa.Column('observed_co2tr', sa.Float(), nullable=True),
        sa.Column('observed_wvtr', sa.Float(), nullable=True),
        sa.Column('observed_product_condition', sa.String(), nullable=True),
        sa.Column('predicted_outputs', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('comparison_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_status', sa.Enum('VALID', 'INVALID', 'PENDING_REVIEW', name='validationstatus'), nullable=False),
        sa.Column('validation_message', sa.String(), nullable=True),
        sa.Column('evidence_source_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('observed_shelf_life_days > 0 OR observed_shelf_life_days IS NULL', name='ck_pfr_shelf_life_pos'),
        sa.CheckConstraint('observed_otr >= 0 OR observed_otr IS NULL', name='ck_pfr_otr_nonneg'),
        sa.CheckConstraint('observed_co2tr >= 0 OR observed_co2tr IS NULL', name='ck_pfr_co2tr_nonneg'),
        sa.CheckConstraint('observed_wvtr >= 0 OR observed_wvtr IS NULL', name='ck_pfr_wvtr_nonneg'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_packaging_feedback_record_recommendation_run_id'), 'packaging_feedback_record', ['recommendation_run_id'], unique=False)
    op.create_index(op.f('ix_packaging_feedback_record_candidate_id'), 'packaging_feedback_record', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_packaging_feedback_record_material_id'), 'packaging_feedback_record', ['material_id'], unique=False)
    op.create_index(op.f('ix_packaging_feedback_record_trial_identifier'), 'packaging_feedback_record', ['trial_identifier'], unique=False)
    op.create_index(op.f('ix_packaging_feedback_record_observation_origin'), 'packaging_feedback_record', ['observation_origin'], unique=False)
    op.create_index(op.f('ix_packaging_feedback_record_validation_status'), 'packaging_feedback_record', ['validation_status'], unique=False)

    op.create_table(
        'model_update_candidate',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('feedback_record_id', sa.UUID(), nullable=False),
        sa.Column('affected_component', sa.String(), nullable=False),
        sa.Column('affected_property', sa.String(), nullable=False),
        sa.Column('prediction_value', sa.Float(), nullable=True),
        sa.Column('prediction_min', sa.Float(), nullable=True),
        sa.Column('prediction_max', sa.Float(), nullable=True),
        sa.Column('observed_value', sa.Float(), nullable=True),
        sa.Column('discrepancy_residual', sa.Float(), nullable=True),
        sa.Column('units', sa.String(), nullable=False),
        sa.Column('interval_status', sa.Enum('MATCHED_WITHIN_INTERVAL', 'OUTSIDE_PREDICTION_INTERVAL', 'OBSERVED_ONLY', 'PREDICTION_ONLY', 'UNKNOWN', name='comparisonstatus'), nullable=False),
        sa.Column('update_status', sa.Enum('NOT_REVIEWED', 'REVIEW_REQUIRED', 'ACCEPTED_FOR_UPDATE', 'REJECTED', 'APPLIED', name='modelupdatestatus'), nullable=False),
        sa.Column('human_review_required', sa.Boolean(), nullable=False),
        sa.Column('discrepancy_evidence_summary', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['feedback_record_id'], ['packaging_feedback_record.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_update_candidate_feedback_record_id'), 'model_update_candidate', ['feedback_record_id'], unique=False)
    op.create_index(op.f('ix_model_update_candidate_affected_component'), 'model_update_candidate', ['affected_component'], unique=False)
    op.create_index(op.f('ix_model_update_candidate_affected_property'), 'model_update_candidate', ['affected_property'], unique=False)
    op.create_index(op.f('ix_model_update_candidate_interval_status'), 'model_update_candidate', ['interval_status'], unique=False)
    op.create_index(op.f('ix_model_update_candidate_update_status'), 'model_update_candidate', ['update_status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('model_update_candidate')
    op.drop_table('packaging_feedback_record')
