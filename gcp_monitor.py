from google.cloud import monitoring_v3
import asyncio
import time
import yaml
import threading

with open('config.yml', 'r') as f:
    doc = yaml.safe_load(f)
METRIC_PREFIX = doc["metricPrefix"]
SUBSCRIPTION_ID = doc["credentials"]["subscriptionId"]
PROJECT = doc["project"]
SERVICES = doc["services"]

print("******Config***********")
print("MetricPrefix",METRIC_PREFIX)
print("SubscriptionId",SUBSCRIPTION_ID)
print("Project:",PROJECT)
print("Services:",SERVICES)
print("******Process********")

apiCallCounter = 0
metricCounter = 0
exitFlag = 0
project = PROJECT
METRIC_PREFIX = METRIC_PREFIX + '|' + PROJECT
client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project}"
metric_list = []


def list_metric_descriptors():
    for descriptor in client.list_metric_descriptors(name=project_name):
        print(descriptor.type)
        metric_list.append(descriptor.type)

class myThread (threading.Thread):
   def __init__(self, metric_list,nspace,labels,exclLabels):
      threading.Thread.__init__(self)
      self.metric_list = metric_list
      self.nspace = nspace
      self.labels = labels
      self.exclLabels = exclLabels
   def run(self):
      print ("Starting " + self.name)
      for m in self.metric_list:
          if m.startswith(self.nspace):
              list_time_series(m,self.nspace,self.labels,self.exclLabels)
      print ("Exiting " + self.name)

def print_time(m,nspace,labels,exclLabels):
    print('----',m,nspace,labels,exclLabels)

def list_time_series(m,nspace,labels,exclLabels):
    print(m,nspace,labels,exclLabels,'******************')
    global apiCallCounter
    global metricCounter
    interval = monitoring_v3.TimeInterval()
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds},
            "start_time": {"seconds": (seconds - 240)},
        }
    )
    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": f'metric.type = "{m}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )
    apiCallCounter += 1
    for result in results:
        #print(result.resource.labels, result.metric.labels, result.resource.type, result.metric.type, result.points[0].value.double_value, result.points[0].value.int64_value)
        label_path = ''
        for l in labels:
            if result.metric.labels[l]:
                label_path = label_path + '|' + result.metric.labels[l]
            elif result.resource.labels[l]:
                label_path = label_path + '|' + result.resource.labels[l]
        p = nspace.replace("/","|") + label_path + m.partition(nspace)[2].replace("/","|")
        for excl in exclLabels:
            if excl and excl in p:
                continue
            else:
                if result.points[0].value.double_value:
                    val = result.points[0].value.double_value
                elif result.points[0].value.int64_value:
                    val = result.points[0].value.int64_value
                print('name='+METRIC_PREFIX+'|'+p+',value='+f'{int(val)}')
                metricCounter += 1

def main():
    threads = []
    list_metric_descriptors()
    for svc in SERVICES:
        thread1 = myThread(metric_list,svc['namespace'],svc['label'],svc['excludeLabels'])
        thread1.start()
        threads.append(thread1)

    for thread in threads:
        thread.join()


    print ("Exiting Main Thread")
    print("API Calls: " , apiCallCounter)
    print("Metrics sent: " , metricCounter)
    print('name='+METRIC_PREFIX+'|extensionAPICalls,value='+f'{apiCallCounter}')
    print('name='+METRIC_PREFIX+'|metrics_uploaded,value='+f'{metricCounter}')


if __name__ == '__main__':
   main()

