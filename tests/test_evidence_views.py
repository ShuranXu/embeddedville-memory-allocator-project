import csv
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project_tools", ROOT / "tools" / "project.py")
PROJECT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(PROJECT)


class EvidenceViewTests(unittest.TestCase):
    def test_linux_views_are_derived_and_digest_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = pathlib.Path(directory)
            (evidence / "kmem-trace.txt").write_text(
                "x: kmalloc: bytes_req=96 bytes_alloc=128\n"
                "x: mm_page_alloc: order=0\n"
            )
            (evidence / "buddyinfo.txt").write_text(
                "Node 0, zone DMA32 1 2 3\n"
            )
            (evidence / "slabinfo.txt").write_text("slabinfo\n")
            (evidence / "slabinfo-extended.txt").write_text("extended\n")

            PROJECT.write_linux_views(evidence)

            with (evidence / "kmalloc-request-table.csv").open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows, [{"requestedBytes": "96", "allocatedBytes": "128", "roundingBytes": "32"}])
            self.assertIn("0,DMA32,2,3,12", (evidence / "buddy-orders.csv").read_text())
            summary = json.loads((evidence / "linux-observation-summary.json").read_text())
            self.assertEqual(summary["kernel"]["version"], "7.2.13")
            self.assertEqual(summary["timelineEvents"], 2)
            self.assertEqual(set(summary["sourceDigests"]), {
                "slabinfo.txt", "slabinfo-extended.txt", "buddyinfo.txt", "kmem-trace.txt",
            })


if __name__ == "__main__":
    unittest.main()
