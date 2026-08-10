import inspect
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
    rdma=0,
    rdma_network_label_id=None,
    rdma_network_selections=None,
):
    pass


class TestAddRdmaLaunchArgs(unittest.TestCase):
    def test_adds_rdma_params_when_supported(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(
            args,
            _launch_workers_with_rdma,
            rdma=2,
            rdma_network_label_id=10,
            rdma_network_selections=[{"network_label_id": 10, "quantity": 2}],
        )
        self.assertEqual(args["rdma"], 2)
        self.assertEqual(args["rdma_network_label_id"], 10)
        self.assertEqual(
            args["rdma_network_selections"],
            [{"network_label_id": 10, "quantity": 2}],
        )

    def test_omits_zero_rdma(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(
            args,
            _launch_workers_with_rdma,
            rdma=0,
            rdma_network_label_id=10,
        )
        self.assertNotIn("rdma", args)
        self.assertEqual(args["rdma_network_label_id"], 10)

    def test_skips_rdma_params_when_unsupported(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(
            args,
            _launch_workers_without_rdma,
            rdma=2,
            rdma_network_label_id=10,
            rdma_network_selections=[{"network_label_id": 10, "quantity": 2}],
        )
        self.assertEqual(args, {"n": 1, "cpu": 2, "memory": 4})

    def test_omits_none_optional_params(self):
        args = {"n": 1, "cpu": 2, "memory": 4}
        add_rdma_launch_args(args, _launch_workers_with_rdma, rdma=2)
        self.assertEqual(args["rdma"], 2)
        self.assertNotIn("rdma_network_label_id", args)
        self.assertNotIn("rdma_network_selections", args)


if __name__ == "__main__":
    unittest.main()
