# Software-Load-balancer
This project implements a simple load balancer using Flask in Python. The load balancer distributes incoming requests among a pool of backend servers using a round-robin or least-connecitonsalgorithm while also performing health checks on those servers.

## Features

- **Round-Robin Load Balancing**: Incoming requests are distributed among available servers in a sequential manner to ensure even utilization.
- **Least Connections Load Balancing**: Incoming requests are forwarded to server with least active connections.
- **Health Checks**: Periodic health checks are performed on backend servers to ensure they are responsive and healthy.
- **Dynamic Server Management**: API endpoints are provided to dynamically upload and delete available servers from the load balancer.

## Load Balancing Algorithms:
- Round Robin: The load balancer iterates through a group of backend-servers, dispatching requests to each one sequentially. Once it reaches the end of the list, it loops back to the beginning to continue the cycle. Round Robin is a static load balancing algorithm.
- Least Connections (default): This method directs traffic towards the server with the least active connections. This is particularly beneficial in scenarios where the duration to process requests can fluctuate significantly. Least Connections is a dynamic load balancing algorithm.

## How to Use

1. **Installation**: Clone the repository and install the required dependencies using `pip`:
    ```
    pip install -r requirements.txt
    ```

2. **Configuration**: Configure the load balancer by editing the `config.json` file. Specify the health check interval, server URLs, and the listening port.

3. **Run the Load Balancer**: Start the load balancer by running the main file:
    ```
    python load_balancer.py
    ```

4. **API Endpoints**:
    - `POST /upload_server`: Upload a new server to the load balancer.
    - `DELETE /delete_server`: Delete a server from the load balancer.

5. **Usage**: Send requests to the load balancer's root endpoint (`/`) to have them distributed among the available servers.

## File Structure

- `main.py`: Main file containing the load balancer implementation.
- `config.json`: Configuration file specifying health check interval, server URLs, listening port, and load balancing algorithm.
- `README.md`: Documentation file.
- `requirements.txt`: List of dependencies.




