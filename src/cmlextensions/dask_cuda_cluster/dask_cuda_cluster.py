#****************************************************************************
# (C) Cloudera, Inc. 2020-2023
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# #  Author(s): Paul de Fusco
#***************************************************************************/

import os
import cdsw

DEFAULT_DASHBOARD_PORT = os.environ["CDSW_APP_PORT"]


class DaskCudaCluster:
    """Dask Cluster built on CML Worker infrastructure"""

    def __init__(
        self,
        num_workers,
        worker_cpu,
        worker_memory,
        scheduler_cpu,
        scheduler_memory,
        dashboard_port=DEFAULT_DASHBOARD_PORT,
    ):
        self.num_workers = num_workers
        self.worker_cpu = worker_cpu
        self.worker_memory = worker_memory
        self.scheduler_cpu = scheduler_cpu
        self.scheduler_memory = scheduler_memory
        self.dashboard_port = dashboard_port

        self.dask_scheduler_details = None
        self.dask_worker_details = None

    def _start_dask_scheduler(self):
        dask_scheduler_cmd = f"!dask scheduler --host 0.0.0.0 --dashboard-address 127.0.0.1:{self.dashboard_port}"

        args = {
            'n': 1,
            'cpu': self.scheduler_cpu,
            'memory': self.scheduler_memory,
            'code': dask_scheduler_cmd,
        }

        if hasattr(cdsw.launch_workers, 'name'):
            args['name'] = 'Dask Scheduler'

        dask_scheduler = cdsw.launch_workers(**args)

        self.dask_scheduler_details = cdsw.await_workers(
            dask_scheduler, wait_for_completion=False, timeout_seconds=600
        )

    def _add_dask_workers(self, scheduler_addr):
        worker_start_cmd = f"!dask cuda worker {scheduler_addr}"

        args = {
            'n': self.num_workers,
            'cpu': self.worker_cpu,
            'memory': self.worker_memory,
            'code': worker_start_cmd,
        }

        if hasattr(cdsw.launch_workers, 'name'):
            args['name'] = 'Dask Cuda Worker'

        dask_workers = cdsw.launch_workers(**args)

        self.dask_worker_details = cdsw.await_workers(
            dask_workers, wait_for_completion=False
        )

    def get_client_url(self):
        dask_scheduler_ip = self.dask_scheduler_details["workers"][0]["ip_address"]
        return f"tcp://{dask_scheduler_ip}:8786"

    def init(self):
        """
        Creates a Dask Cluster on the CML Workers infrastructure.
        """
        try:
            import dask  # pylint: disable=unused-import
        except ImportError as error:
            raise ImportError(
                "Could not import dask, for this module to work please run `pip install dask[complete]` \n -> "
                + str(error)
            ) from error

        # Start the dask scheduler process
        self._start_dask_scheduler()

        dask_scheduler_addr = self.get_client_url()

        self._add_dask_workers(dask_scheduler_addr)

        # TODO: could add cluster details, e.g., worker count and resources
        print(
            f"""
--------------------
Dask cluster started
--------------------

The Dask dashboard is running at
{self.get_dashboard_url()}

To connect to this Dask cluster from this CML Session,
use the following Python code:
  from dask.distributed import Client
  client = Client('{self.get_client_url()}')
"""
        )

    def get_dashboard_url(self):
        """
        Return the Dask dashboard url.
        """
        try:
            return self.dask_scheduler_details["workers"][0]["app_url"] + "status"
        except Error as error:
            raise Error("ERROR: Dask Cuda cluster is not running!")

    def terminate(self):
        """
        Terminates the Dask Cuda Cluster.
        """

        # TODO: stop workers only when they were created for this Dask Cluster
        cdsw.stop_workers()

        # Reset instance state
        self.dask_scheduler_ip = None
        self.dask_scheduler_addr = None
        self.dask_scheduler_details = None
        self.dask_worker_details = None
