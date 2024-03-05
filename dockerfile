# Use a Linux base image as base image for building
FROM alpine:3.17 as builder

# Set the working directory in the container
WORKDIR /app

# Create a non-root user for security
RUN adduser -D myuser

# Copy only the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire code directory into the container
COPY . .

# Compile the Python code to binary using pyinstaller
RUN pyinstaller --onefile load_balancer.py

# Switch to the non-root user
USER myuser

# Final image stage, using the same Alpine image
FROM alpine:3.17

# Copy the compiled binary from the builder stage
COPY --from=builder /app/dist/main /app/main

# Set the working directory
WORKDIR /app

# Expose the port
EXPOSE 5000

# Run the compiled binary
CMD ["./load_balancer"]