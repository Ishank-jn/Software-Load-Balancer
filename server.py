import threading
import urllib.parse
import syslog
import requests
import time
from http.server import SimpleHTTPRequestHandler

class Server:
    def __init__(self, url):
        """
        Initializes a Server object with the provided URL.
        
        Args:
            url (str): The URL of the server.
        """
        self.URL = urllib.parse.urlparse(url)
        self.ActiveConnections = 0
        self.Mutex = threading.Lock()
        self.Healthy = False

    def start_health_check(self, interval):
        """Starts a periodic health check thread for the server.

        Args:
            interval (int): The interval (in seconds) between health checks.
        """
        self.health_check_thread = threading.Thread(target=self.health_check, args=(interval), daemon=True)
        self.health_check_thread.start()

    def stop_health_check(self):
        """Stops the running health check thread, if any.

        Waits for the thread to finish before returning.
        """
        if self.health_check_thread:
            self.health_check_thread.join()

    def health_check(self, interval):
        """Performs a health check on the server at a regular interval.

        Sends an HTTP GET request to the server's URL and updates the server's
        `Healthy` attribute based on the response status code. Logs errors using syslog.

        Args:
            interval (int): The interval (in seconds) between health checks.
        """
        while True:
            try:
                response = requests.get(self.URL.geturl())
                self.Healthy = response.status_code < 500
            except Exception as e:
                self.Healthy = False
                syslog.syslog(syslog.LOG_ERR, f"Health check failed for server {self.URL.geturl()}: {str(e)}")
            time.sleep(interval)
    
    def proxy(self):
        """
        Returns a SimpleHTTPRequestHandler object for proxying requests to the server.
        """
        return SimpleHTTPRequestHandler(self.URL.netloc)