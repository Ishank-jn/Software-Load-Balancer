import json
from config import Config

def load_config(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return Config(data['healthCheckInterval'], data['servers'], data['listenPort'])

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