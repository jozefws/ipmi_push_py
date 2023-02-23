import os
import re
# from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from dotenv import load_dotenv
from influxdb import InfluxDBClient
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
def send_to_database(cpu_temps, psu_watts, hostname):
    body = encode_to_json(cpu_temps, psu_watts, hostname)
    client = database_connection()
    if client.write_points(body):
        print("Data sent to influx")
    else:
        print("Failed to send data to influx")
    client.close()
    return

def encode_to_json(cpu_temps, psu_watts, hostname):
    json_body = []
    cpu_count = 1
    psu_count = 1
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for i in cpu_temps:
        json_body.append({
            "measurement": "cpu_temp",
            "tags": {
                "cpu": str(cpu_count),
                "host": hostname
            },
            "time": {timestamp},
            "fields": {
                "value": float(i[:-1])
            }
        })
        cpu_count+=1

    for i in psu_watts:
        json_body.append({
            "measurement": "psu_watts",
            "tags": {
                "psu": str(psu_count),
                "host": hostname
            },
             "time": {timestamp},
            "fields": {
                "value": float(i[:-1])
            }
        })
        psu_count+=1
    print(json_body)
    return json_body

def database_connection():
    load_dotenv()
    client = InfluxDBClient(
        host=os.getenv("INFLUX_HOST"),
        port=os.getenv("INFLUX_PORT"),
        username=os.getenv("INFLUX_USER"),
        password=os.getenv("INFLUX_PASS"),
        ssl=os.getenv("INFLUX_SSL"),
        verify_ssl=os.getenv("INFLUX_VERIFY_SSL"),
    )
    client.switch_database(os.getenv("INFLUX_DB_NAME"))
    return client

    

if __name__ == '__main__':
    cpu_temps, psu_watts = run_ipmi_sensors()
    hostname = get_hostname()
    send_to_database(cpu_temps, psu_watts, hostname)


