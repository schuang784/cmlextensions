# Copyright 2026 Cloudera. All Rights Reserved.
#
# This file is licensed under the Apache License Version 2.0
# (the "License"). You may not use this file except in compliance
# with the License. You may obtain  a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. Refer to the
# License for the specific permissions and limitations governing your
# use of the file.

import inspect


def add_rdma_launch_args(
    args,
    launch_workers_fn,
    rdma_network_selections=None,
):
    """Add RDMA network selections to launch_workers args when supported by the API."""
    params = inspect.signature(launch_workers_fn).parameters
    if "rdma_network_selections" in params and rdma_network_selections is not None:
        args["rdma_network_selections"] = rdma_network_selections
    return args
