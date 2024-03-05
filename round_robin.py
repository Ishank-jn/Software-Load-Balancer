import threading

class RoundRobin:
    def __init__(self, servers):
        """
        Initializes the RoundRobin load balancer with the provided list of servers.
        
        Args:
            servers (list): A list of Server objects representing backend servers.
        """
        self.servers = servers
        self.current_index = 0
        self.mutex = threading.Lock()

    def get_next_server(self):
        """
        Selects the next server in a round-robin manner.

        Returns:
            Server: The next server to handle the request.
        """
        # with self.mutex:
        #     server = self.servers[self.current_index]
        #     self.current_index = (self.current_index + 1) % len(self.servers)
        # return server

        with self.mutex:  # Acquire the lock
            num_servers = len(self.servers)
            start_index = self.current_index  # Store the initial index
            while True:
                server = self.servers[self.current_index]  # Get the server at the current index
                self.current_index = (self.current_index + 1) % num_servers  # Move to the next server in the list
                if server.Healthy:  # Check if the server is healthy
                    return server  # Return the selected healthy server
                # If we've checked all servers and haven't found a healthy one, break the loop
                if self.current_index == start_index:
                    break
        # If no healthy server is found, return None
        return None