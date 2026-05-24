from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StarterRequirementTests(unittest.TestCase):
    def test_starter_db_and_review_brief_include_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "starter-product"
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "create_starter_project.py"), "--target", str(target)],
                cwd=ROOT,
                check=True,
            )
            subprocess.run([sys.executable, str(target / "tools" / "init_project_db.py")], cwd=target, check=True)
            subprocess.run(
                [sys.executable, str(target / "tools" / "generate_review_brief.py"), "--record-db"],
                cwd=target,
                check=True,
            )

            conn = sqlite3.connect(target / ".aivprocess" / "project.db")
            try:
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM requirement_item").fetchone()[0],
                    3,
                )
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM requirement_classification").fetchone()[0],
                    27,
                )
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM requirement_allocation").fetchone()[0],
                    3,
                )
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM requirement_trace").fetchone()[0],
                    9,
                )
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM reuse_assessment").fetchone()[0],
                    3,
                )
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM feedback_item").fetchone()[0],
                    2,
                )
                self.assertEqual(
                    conn.execute(
                        """
                        SELECT COUNT(*)
                        FROM requirement_item
                        WHERE requirement_type = 'nonfunctional'
                          AND constraint_origin IN ('architecture_constraint','human_factors_constraint')
                        """
                    ).fetchone()[0],
                    2,
                )
            finally:
                conn.close()

            brief = next((target / "docs").glob("review_brief_*.md"))
            text = brief.read_text(encoding="utf-8")
            self.assertIn("## Requirement Summary", text)
            self.assertIn("### Nonfunctional Constraint Origins", text)
            self.assertIn("### Requirement Classification Coverage", text)
            self.assertIn("### Requirement Allocation Coverage", text)
            self.assertIn("### Requirement Trace Coverage", text)
            self.assertIn("### Requirement Gap Counters", text)
            self.assertIn("## Reuse And Delta Summary", text)
            self.assertIn("## Feedback And Feasibility Summary", text)
            self.assertIn("NO-EXISTING-TEST-AS-REVALIDATION", text)
            self.assertIn("NO-FEEDBACK-AS-REQUIREMENT", text)
            self.assertIn("NO-IMPLEMENTATION-AS-VALIDATION", text)


if __name__ == "__main__":
    unittest.main()
