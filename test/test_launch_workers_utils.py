import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cmlextensions.launch_workers_utils import add_rdma_launch_args


def _launch_workers_without_rdma(n, cpu, memory, nvidia_gpu=0, code=""):
    pass


def _launch_workers_with_rdma(
    n,
    cpu,
    memory,
    nvidia_gpu=0,
    code="",
    rdma_network_selections=None,
):
    pass


class TestAddRdmaLaunchArgs(unittest.TestCase):
    def test_adds_rdma_network_selections_when_supported(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        selections = [{"network_label_id": 10, "quantity": 2}]
        add_rdma_launch_args(
            args,
            _launch_workers_with_rdma,
            rdma_network_selections=selections,
        )
        self.assertEqual(args["rdma_network_selections"], selections)
        self.assertNotIn("rdma", args)

    def test_skips_rdma_network_selections_when_unsupported(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(
            args,
            _launch_workers_without_rdma,
            rdma_network_selections=[{"network_label_id": 10, "quantity": 2}],
        )
        self.assertEqual(args, {"n": 1, "cpu": 2, "memory": 4})

    def test_omits_none_rdma_network_selections(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(args, _launch_workers_with_rdma)
        self.assertNotIn("rdma_network_selections", args)
        self.assertNotIn("rdma", args)


if __name__ == "__main__":
    unittest.main()
