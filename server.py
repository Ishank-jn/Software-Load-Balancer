import threading
import urllib.parse
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
    
    def proxy(self):
        """
        Returns a SimpleHTTPRequestHandler object for proxying requests to the server.
        """
        return SimpleHTTPRequestHandler(self.URL.netloc)