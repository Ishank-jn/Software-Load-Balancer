################
# Load Balancer
################

import threading
import requests
import syslog
import datetime
import signal
import sys
from flask import Flask, request, Response
from prometheus_client import start_http_server, Counter, Gauge
from server import Server
from round_robin import RoundRobin
from utility import load_config, next_server_least_active

app = Flask(__name__)

# Prometheus metrics
REQUESTS_TOTAL = Counter('http_requests_total', 'Total number of HTTP requests')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
# if using round robin LB
round_robin = None
# Backend server List
servers = []
# check for new servers
update_server_list = False
# Store the currently configured load balancing algorithm
lb_type = None

@app.route('/')
def proxy_request():
    """
        Routes incoming requests to the appropriate server based on the load balancing algorithm.
    """
    global lb_type, servers

    if lb_type == "least_connections":
        # Select the server with the least active connections
        server = next_server_least_active(servers)
        # Acquire the server's mutex to manage active connections
        with server.Mutex:
            server.ActiveConnections += 1

        ACTIVE_CONNECTIONS.inc()
        REQUESTS_TOTAL.inc()

        # Forward to appropiate backend server
        response = requests.get(server.URL.geturl() + request.full_path, timeout=5)
        # Release the server's mutex
        with server.Mutex:
            server.ActiveConnections -= 1

        syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Request handled by {server.URL.geturl()} - \
                      Status code: {response.status_code}")
        ACTIVE_CONNECTIONS.dec()
        return response.content, response.status_code
    
    elif lb_type == "round_robin":
        global round_robin, update_server_list
        # Select next server in round robin order
        server = round_robin.get_next_server()
        if not round_robin or update_server_list:
            round_robin.update_servers(servers)
            update_server_list = False

        ACTIVE_CONNECTIONS.inc()
        REQUESTS_TOTAL.inc
        
        if not server:
            ACTIVE_CONNECTIONS.dec()
            return Response("Internal Server Error", status=500)

        # Forward to appropiate backend server
        response = requests.get(server.URL.geturl() + request.full_path)

        syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Request handled by {server.URL.geturl()} - \
                      Status code: {response.status_code}")
        ACTIVE_CONNECTIONS.dec()
        return response.content, response.status_code
    else:
        syslog.syslog(syslog.LOG_ERR, f"[{datetime.now()}] Load Balancer not configured properly")
        return Response("LB config Error", status=500)

@app.route('/upload_server', methods=['POST'])
def upload_server():
    """
    Endpoint to upload a new server to the load balancer.
    Expects JSON data in the request body with the server URL.
    """
    global upload_server_list, servers
    data = request.json
    new_server_url = data.get('url')
    if new_server_url:
        upload_server_list = True
        new_server = Server(new_server_url)
        servers.append(new_server)
        new_server.start_health_check(config.HealthCheckInterval)  # Start health check thread for new server
        return {'message': 'Server uploaded successfully'}, 200
    else:
        return {'error': 'URL not provided'}, 400

@app.route('/delete_server', methods=['DELETE'])
def delete_server():
    """
    Endpoint to delete a server from the load balancer.
    Expects JSON data in the request body with the server URL.
    """
    global update_server_list, servers
    data = request.json
    server_url_to_delete = data.get('url')
    if server_url_to_delete:
        for server in servers:
            if server.URL.geturl() == server_url_to_delete:
                server.stop_health_check()  # Stop health check thread for the server
                servers.remove(server)
                update_server_list = True
                return {'message': 'Server deleted successfully'}, 200
        return {'error': 'Server not found'}, 404
    else:
        return {'error': 'URL not provided'}, 400


def signal_handler(sig, frame):
    syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Received termination signal. Shutting down gracefully.")
    sys.exit(0)

if __name__ == "__main__":
    # Load LB config
    config = load_config("config.json")
    health_check_interval = int(config.HealthCheckInterval)
    lb_type = config.LBAlgorithm

    servers = [Server(server_url) for server_url in config.Servers]
    # Start health check on the servers
    for server in servers:
        server.start_health_check()

    # Initialize round_robin object only if the algorithm is set to round_robin
    if not round_robin and lb_type == 'round_robin':
        round_robin = RoundRobin(servers)

    # open log
    syslog.openlog(ident="LoadBalancer", logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Starting server on port {config.ListenPort}")

     # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start Prometheus metrics server
    start_http_server(8000)  # Expose metrics on port 8000
    
    app.run(port=int(config.ListenPort))

    # Close syslog connection (would be automatically closed at program exit)
    syslog.closelog()
