import os
import re
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from datetime import datetime
 
# Run ipmi command and return the output
def run_ipmi_sensors():
    stream = os.popen("sudo ipmi-sensors --sensor-types=Temperature,Power_Supply --comma-separated-output --ignore-not-available-sensors --no-header-output")
    output = stream.read()

    cpu_temps = []
    psu_watts = []

    for i in output.split('\n'):
        j = i.split(',')
        try:
            if(re.search('CPU[0-9] Temperature', j[1])):
                cpu_temps.append(j[3] + "c")
            elif("PMBPower" in j[1]):
                psu_watts.append(j[3]+ "W")
        except:
            pass
    return cpu_temps, psu_watts

# Get the hostname
def get_hostname():
    stream = os.popen("hostname")
    output = stream.read()
    return output

def to_dict(cpu_temps, psu_watts, hostname):
    dict = []
    cpu_count = 1
    psu_count = 1
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for i in cpu_temps:
        dict.append({
            "measurement": "cpu_temp",
            "tags": {
                "host": hostname,
                "cpu": cpu_count
            },
            "fields": {
                "value": i
            },
            "time": timestamp
        })
        cpu_count += 1

    for i in psu_watts:
        dict.append({
            "measurement": "psu_watt",
            "tags": {
                "host": hostname,
                "psu": psu_count
            },
            "fields": {
                "value": i
            },
            "time": timestamp
        })
        psu_count += 1
    
    return dict

# Send to localhost influx database
def send_to_influx(dict):
    print(os.getenv("INFLUX_URL"))
    print(os.getenv("INFLUX_PORT"))
    url_port = os.getenv("INFLUX_URL") + ":" + os.getenv("INFLUX_PORT")
    print(url_port)
    client = InfluxDBClient(
        url=url_port,
        token=os.getenv("INFLUX_TOKEN"),
        org=os.getenv("INFLUX_ORG"),
        verify_ssl=False
    )

    with client:
        try:
            client.write_api(write_options=SYNCHRONOUS).write(bucket=os.getenv("INFLUX_BUCKET"), record=dict)
        except InfluxDBError as e:
            print(e)

    

if __name__ == '__main__':
    cpu_temps, psu_watts = run_ipmi_sensors()
    hostname = get_hostname()
    data = to_dict(cpu_temps, psu_watts, hostname)
    send_to_influx(data)


