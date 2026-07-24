from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sqlite3
import unittest

from saas_retention.pipeline import parse_queries, run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RetentionPipelineTest(unittest.TestCase):
    def test_sql_blocks_are_named(self) -> None:
        queries = parse_queries((PROJECT_ROOT / "sql" / "analysis.sql").read_text(encoding="utf-8"))
        self.assertEqual(
            set(queries),
            {
                "headline_kpis",
                "monthly_trend",
                "segment_health",
                "channel_health",
                "cohort_retention",
                "risk_segments",
            },
        )

    def test_end_to_end_pipeline(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sql").mkdir()
            shutil.copy2(PROJECT_ROOT / "sql" / "analysis.sql", root / "sql" / "analysis.sql")
            result = run_pipeline(root, seed=42)
            self.assertEqual(result["summary"]["status"], "ready_to_share")
            self.assertTrue(result["artifact"].exists())
            self.assertTrue(result["dashboard"].exists())
            dashboard = result["dashboard"].read_text(encoding="utf-8")
            self.assertIn("Retention Command Center", dashboard)
            self.assertIn("window.__DASHBOARD_DATA__", dashboard)
            self.assertEqual(len(result["results"]["monthly_trend"]), 12)
            headline = result["results"]["headline_kpis"].iloc[0]
            self.assertGreater(float(headline["mrr"]), 0)
            self.assertEqual(headline["as_of_date"], "2025-12-31")

            cohort = result["results"]["cohort_retention"]
            self.assertEqual(len(cohort), cohort["cohort_month"].nunique() * 7)
            self.assertTrue(cohort["retention_rate"].between(0, 1).all())
            self.assertTrue(
                cohort.groupby("cohort_month")["month_number"].nunique().eq(7).all()
            )

            connection = sqlite3.connect(root / "data" / "analytics.db")
            try:
                eligible_14 = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM accounts
                    WHERE signup_date <= DATE('2025-12-31', '-14 day')
                    """
                ).fetchone()[0]
                eligible_30 = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM accounts
                    WHERE signup_date <= DATE('2025-12-31', '-30 day')
                    """
                ).fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(int(headline["eligible_accounts"]), eligible_14)
            self.assertEqual(int(headline["eligible_trials"]), eligible_30)


if __name__ == "__main__":
    unittest.main()
