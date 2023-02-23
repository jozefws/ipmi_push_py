import os
import re
# from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
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

# Send to localhost influx database
def send_to_database(body):
    client = database_connection()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    result = write_api.write(bucket = os.getenv("INFLUX_BUCKET"), org= os.getenv("INFLUX_ORG"), dict=body)
    print(result)
    client.close()
    return

def encode_to_dict(cpu_temps, psu_watts, hostname):
    cpu_count = 1
    psu_count = 1
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for i in cpu_temps:
        cpu_body ={
            "measurement": "cpu_temp",
            "tags": {
                "host": hostname,
                "cpu": cpu_count
            },
            "fields": {
                "value": i
            },
            "time": timestamp
        }
        cpu_count += 1
        send_to_database(cpu_body)

    for i in psu_watts:
        psu_body={
            "measurement": "psu_watt",
            "tags": {
                "host": hostname,
                "psu": psu_count
            },
            "fields": {
                "value": i
            },
            "time": timestamp
        }
        psu_count += 1
        send_to_database(psu_body)


def database_connection():
    load_dotenv()
    client = InfluxDBClient(
        url=os.getenv("INFLUX_URL")+":"+os.getenv("INFLUX_PORT"),
        token=os.getenv("INFLUX_TOKEN"),
        org=os.getenv("INFLUX_ORG"),
        verify_ssl=os.getenv("INFLUX_VERIFY_SSL"),
    )
    return client

    

if __name__ == '__main__':
    cpu_temps, psu_watts = run_ipmi_sensors()
    hostname = get_hostname()
    encode_to_dict(cpu_temps, psu_watts, hostname)


