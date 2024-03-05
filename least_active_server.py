def next_server_least_active(servers):
    """
    Selects the server with the least active connections among the healthy servers.

    Args:
        servers (list): A list of Server objects representing backend servers.

    Returns:
        Server: The server with the least active connections among the healthy servers.
    """
    least_active_connections = -1
    least_active_server = servers[0]
     # Iterate through each server to find the one with the least active connections
    for server in servers:
        with server.Mutex:
            if (server.ActiveConnections < least_active_connections or least_active_connections == -1) and server.Healthy:
                least_active_connections = server.ActiveConnections
                least_active_server = server
    
    return least_active_server
