# gcpappd
AppD Extension to Pull GCP Metrics

Custom extension to get GCP service metrics using Google Cloud Monitoring API (python library)

Works for any GCP metric/service

# Prerequisites

Install python library (Python 3+)

pip3 install --upgrade google-cloud-monitoring

pip3 install pyyaml==5.4.1

# Install & Configuration

1. Install as Machine Agent Custom Extension (Bundle all files into GCPMonitor folder and copy to machine agent monitors folder)
2. Update env variable (GOOGLE_APPLICATION_CREDENTIALS) in gcp_monitor.sh to point to location of access key file.
3. Configure config.yml
