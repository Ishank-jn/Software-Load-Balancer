import json
import time
import requests
import syslog
from config import Config

def load_config(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return Config(data['healthCheckInterval'], data['servers'], data['listenPort'])


def health_check(server, interval):
    while True:
        try:
            response = requests.get(server.URL.geturl())
            server.Healthy = response.status_code < 500
        except Exception as e:
            server.Healthy = False
            syslog.syslog(syslog.LOG_ERR, f"Health check failed for server {server.URL.geturl()}: {str(e)}")
        time.sleep(interval)


def next_server_least_active(servers):
    least_active_connections = -1
    least_active_server = servers[0]
    
    for server in servers:
        with server.Mutex:
            if (server.ActiveConnections < least_active_connections or least_active_connections == -1) and server.Healthy:
                least_active_connections = server.ActiveConnections
                least_active_server = server
    
    return least_active_server
    # Alternative code: 
    # issue: takes 2 for loops (cost) and doesn't take lock
    # healthy_servers = [server for server in servers if server.Healthy]
    # if not healthy_servers:
    #     raise Exception("No healthy servers available")
    # return min(healthy_servers, key=lambda x: x.ActiveConnections)