"""create autoops reporting tables"""

from alembic import op
import sqlalchemy as sa

revision = "001_create_autoops_reporting_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.String(), unique=True, index=True),
        sa.Column("service", sa.String(), index=True),
        sa.Column("source", sa.String(), index=True),
        sa.Column("severity", sa.String(), index=True),
        sa.Column("issue_type", sa.String(), index=True),
        sa.Column("issue_family", sa.String(), index=True),
        sa.Column("symptom", sa.Text()),
        sa.Column("customer_impact", sa.Text()),
        sa.Column("probable_owner", sa.String()),
        sa.Column("recommended_action", sa.Text()),
        sa.Column("escalation_required", sa.Boolean(), default=False),
        sa.Column("status", sa.String(), default="new"),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "service_health",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service", sa.String(), index=True),
        sa.Column("health_status", sa.String()),
        sa.Column("risk_level", sa.String()),
        sa.Column("incident_count", sa.Integer(), default=0),
        sa.Column("escalation_count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime()),
    )

    op.create_table(
        "escalations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.String()),
        sa.Column("escalation_path", sa.Text()),
        sa.Column("owner", sa.String()),
        sa.Column("reason", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "reporting_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_week", sa.String(), index=True),
        sa.Column("total_incidents", sa.Integer()),
        sa.Column("total_escalations", sa.Integer()),
        sa.Column("top_issue_family", sa.String()),
        sa.Column("summary", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
    )

def downgrade():
    op.drop_table("reporting_snapshots")
    op.drop_table("escalations")
    op.drop_table("service_health")
    op.drop_table("incidents")
