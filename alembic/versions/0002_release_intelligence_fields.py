from alembic import op
import sqlalchemy as sa

revision = "0002_release_intelligence_fields"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("analyses", sa.Column("repo_name", sa.String(255), nullable=True))
    op.add_column("analyses", sa.Column("workflow_name", sa.String(255), nullable=True))
    op.add_column("analyses", sa.Column("run_id", sa.String(255), nullable=True))
    op.add_column("analyses", sa.Column("root_cause", sa.String(255), nullable=True))
    op.add_column("analyses", sa.Column("runbook", sa.Text(), nullable=True))
    op.add_column("analyses", sa.Column("runbook_confidence", sa.Float(), nullable=True))
    op.add_column("analyses", sa.Column("release_decision", sa.String(32), nullable=True))
    op.add_column("analyses", sa.Column("decision_confidence", sa.Float(), nullable=True))
    op.add_column("analyses", sa.Column("change_point_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("analyses", sa.Column("recurrence_score", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("analyses", "recurrence_score")
    op.drop_column("analyses", "change_point_flag")
    op.drop_column("analyses", "decision_confidence")
    op.drop_column("analyses", "release_decision")
    op.drop_column("analyses", "runbook_confidence")
    op.drop_column("analyses", "runbook")
    op.drop_column("analyses", "root_cause")
    op.drop_column("analyses", "run_id")
    op.drop_column("analyses", "workflow_name")
    op.drop_column("analyses", "repo_name")
