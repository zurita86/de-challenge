from google.cloud import dataproc_v1
from google.cloud import storage
from google.cloud.dataproc_v1.gapic.transports import (
    job_controller_grpc_transport,
    cluster_controller_grpc_transport,
)
from google.protobuf.duration_pb2 import Duration

d = Duration()
d.FromSeconds(1800)

# parameters
project = 'de-challenge-1'  # GCP project name
cluster_name = 'cluster-tmp-01'  # Dataproc cluster name  (Whatever you want)
region = 'us-central1'
zone = 'us-central1-a'
worker_config = 2  # number of workers


# Trigger function by Storage.
def trigger_spark_job(data, context):
    
    if data['name'] == 'data/result.csv' :

        # 1. Create a cluster
        client_transport = (
            cluster_controller_grpc_transport.ClusterControllerGrpcTransport(
                address='{}-dataproc.googleapis.com:443'.format(region)))

        dataproc_cluster_client = dataproc_v1.ClusterControllerClient(
                client_transport)

        zone_uri = \
            'https://www.googleapis.com/compute/v1/projects/{}/zones/{}'.format(
                project, zone)

        cluster_data = {
            'project_id': project,
            'cluster_name': cluster_name,
            'config': {
                "lifecycle_config": {"idle_delete_ttl": d},
                'gce_cluster_config': {
                    'zone_uri': zone_uri
                },
                'master_config': {
                    'num_instances': 1,
                    'machine_type_uri': 'n1-standard-4'
                },
                'worker_config': {
                    'num_instances': worker_config,
                    'machine_type_uri': 'n1-standard-4'
                },
            }
        }

        cluster = dataproc_cluster_client.create_cluster(project, region, cluster_data)

        # NOTE: CLUSTER MUST BE CREATED THEN ONLY WE CAN SUBMIT JOB
        cluster.add_done_callback(lambda _: submit_job(data))

def submit_job(data):
    print("Starting Jobs...")
    # 2. Submit a job
    bucket = data['bucket']
    python_file = 'gs://' + bucket + '/pipeline/games.py'  # Pipeline code path.
    
    client = storage.Client()
    bucketObj = client.bucket(bucket)
    
    job_transport = (
                job_controller_grpc_transport.JobControllerGrpcTransport(
                    address='{}-dataproc.googleapis.com:443'.format(region)))

    dataproc = dataproc_v1.JobControllerClient(job_transport)
    
    print("List Queries...")
    
    for blob in bucketObj.list_blobs(prefix='queries/'):
        if '.sql' in blob.name:
            print('Query: '+blob.name)

            job_details = {
                'placement': {
                    'cluster_name': cluster_name
                },
                'pyspark_job': {
                    'main_python_file_uri': python_file,
                    'args': [
                        'gs://' + bucket + '/data/',
                        'gs://' + bucket + '/output/',
                        blob.name,
                        bucket
                    ]
                }
            }

            result = dataproc.submit_job(
                project_id=project, region=region, job=job_details)
            job_id = result.reference.job_id

            print('Submitted job ID {}.'.format(job_id))