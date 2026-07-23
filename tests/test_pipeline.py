from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
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
            self.assertEqual(len(result["results"]["monthly_trend"]), 12)
            self.assertGreater(float(result["results"]["headline_kpis"].iloc[0]["mrr"]), 0)


if __name__ == "__main__":
    unittest.main()

