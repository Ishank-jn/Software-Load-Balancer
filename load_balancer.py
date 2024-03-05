##############
# Load Balancer
##############

import threading
import requests
import syslog
import datetime
from flask import Flask, request, Response
from server import Server
from round_robin import RoundRobin
from utility import load_config, health_check, next_server_least_active

app = Flask(__name__)

# if using round robin LB
round_robin = None
# Store the currently configured load balancing algorithm
lb_type = None


@app.route('/')
def proxy_request():
    """
        Routes incoming requests to the appropriate server based on the load balancing algorithm.
    """
    global lb_type

    if lb_type == "least_connections":
        # Select the server with the least active connections
        server = next_server_least_active(servers)
        # Acquire the server's mutex to manage active connections
        with server.Mutex:
            server.ActiveConnections += 1
        # Forward to appropiate backend server
        response = requests.get(server.URL.geturl() + request.full_path)
        # Release the server's mutex
        with server.Mutex:
            server.ActiveConnections -= 1

        syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Request handled by {server.URL.geturl()} - \
                      Status code: {response.status_code}")
        return response.content, response.status_code
    
    elif lb_type == "round_robin":
        global round_robin
        # Select next server in round robin order
        server = round_robin.get_next_server()
        
        if not server:
            return Response("Internal Server Error", status=500)
        # Forward to appropiate backend server
        response = requests.get(server.URL.geturl() + request.full_path)

        syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Request handled by {server.URL.geturl()} - \
                      Status code: {response.status_code}")
        return response.content, response.status_code
    else:
        syslog.syslog(syslog.LOG_ERR, f"[{datetime.now()}] Load Balancer not configured properly")
        pass

@app.route('/upload_server', methods=['POST'])
def upload_server():
    """
    Endpoint to upload a new server to the load balancer.
    Expects JSON data in the request body with the server URL.
    """
    data = request.json
    new_server_url = data.get('url')
    if new_server_url:
        new_server = Server(new_server_url)
        servers.append(new_server)
        return {'message': 'Server uploaded successfully'}, 200
    else:
        return {'error': 'URL not provided'}, 400

@app.route('/delete_server', methods=['DELETE'])
def delete_server():
    """
    Endpoint to delete a server from the load balancer.
    Expects JSON data in the request body with the server URL.
    """
    data = request.json
    server_url_to_delete = data.get('url')
    if server_url_to_delete:
        for server in servers:
            if server.URL.geturl() == server_url_to_delete:
                servers.remove(server)
                return {'message': 'Server deleted successfully'}, 200
        return {'error': 'Server not found'}, 404
    else:
        return {'error': 'URL not provided'}, 400

if __name__ == "__main__":
    # Load LB config
    config = load_config("config.json")
    health_check_interval = int(config.HealthCheckInterval)
    lb_type = config.LBAlgorithm

    servers = [Server(server_url) for server_url in config.Servers]
    # Initialize round_robin object only if the algorithm is set to round_robin
    if not round_robin and lb_type == 'round_robin':
        round_robin = RoundRobin(servers)

    for server in servers:
        threading.Thread(target=health_check, args=(server, health_check_interval), daemon=True).start()

    # open log
    syslog.openlog(ident="LoadBalancer", logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_INFO, f"[{datetime.now()}] Starting server on port {config.ListenPort}")

    app.run(port=int(config.ListenPort))

    # Close syslog connection (would be automatically closed at program exit)
    syslog.closelog()
