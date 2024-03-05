class Config:
    def __init__(self, health_check_interval, servers, listen_port, algorithm = "least_connections"):
        """
        Initialize config object for Load Balancer server.
        """
        self.HealthCheckInterval = health_check_interval
        self.Servers = servers
        self.ListenPort = listen_port
        self.LBAlgorithm = algorithm