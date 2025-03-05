# Add cmlextensions to the path
import sys
sys.path.append('../src')

#from dask_cuda import LocalCUDACluster
from src.cmlextensions.dask_cuda_cluster.dask_cuda_cluster import DaskCudaCluster

cluster = DaskCudaCluster(num_workers=2, worker_cpu=4, nvidia_gpu=2, worker_memory=12, scheduler_cpu=4, scheduler_memory=12)
cluster.init()

# Connect to the cluster
from dask.distributed import Client
client = Client(cluster.get_client_url())

client

import dask.array as da

# Create a dask array from a NumPy array
x = da.from_array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], chunks=(2, 2))

# Perform a computation on the dask array
y = (x + 1) * 2

# Submit the computation to the cluster for execution
future = client.submit(y.compute)

# Wait for the computation to complete and retrieve the result
result = future.result()

print(result)  # Outputs: [[ 4  6  8] [10 12 14] [14 16 18]]

# Delete cluster
#cluster.terminate()
