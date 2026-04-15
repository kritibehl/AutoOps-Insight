from __future__ import annotations

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from storage.db.base import DBClient

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://autoops:autoops@localhost:5433/autoops",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class PostgresClient(DBClient):
    def insert_analysis(self, data):
        with SessionLocal() as session:
            session.execute(
                text(
                    """
                    INSERT INTO analyses (
                        signature,
                        failure_family,
                        severity,
                        summary,
                        repo_name,
                        workflow_name,
                        run_id,
                        root_cause,
                        runbook,
                        runbook_confidence,
                        release_decision,
                        decision_confidence,
                        change_point_flag,
                        recurrence_score
                    ) VALUES (
                        :signature,
                        :failure_family,
                        :severity,
                        :summary,
                        :repo_name,
                        :workflow_name,
                        :run_id,
                        :root_cause,
                        :runbook,
                        :runbook_confidence,
                        :release_decision,
                        :decision_confidence,
                        :change_point_flag,
                        :recurrence_score
                    )
                    """
                ),
                data,
            )
            session.commit()

    def fetch_recent(self, limit):
        with SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    SELECT *
                    FROM analyses
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            )
            return [dict(r._mapping) for r in result]

    def fetch_by_signature(self, signature):
        with SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    SELECT *
                    FROM analyses
                    WHERE signature = :signature
                    ORDER BY created_at DESC
                    """
                ),
                {"signature": signature},
            )
            return [dict(r._mapping) for r in result]

    def fetch_recent_by_repo(self, repo_name, limit=50):
        with SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    SELECT *
                    FROM analyses
                    WHERE repo_name = :repo_name
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"repo_name": repo_name, "limit": limit},
            )
            return [dict(r._mapping) for r in result]
