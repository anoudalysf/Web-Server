# Basic Web Server with Advanced Python Features

## Project Structure

The project consists of two main files:

- **webserver.py**: Contains the implementation of the web server, you would need to first run this file to initiate the server in order for the client to connect to it after.
- **client.py**: Simulates client requests to the server which in turn gains responses from the server, this file will be ran after the server has been initiated.

### Decorators

- **`log_request`**: Logs incoming requests with timestamp and data payload.
- **`authorize_request`**: Verifies the presence and correctness of an authorization token, could be tested in the clients side by once giving it the valid auth_token, then test an invalidness by giving it an incorrect token.

### Generators

- **`response_generator`**: Dynamically generates HTTP responses based on provided data.
- **`stream_data`**: Implements a generator for streaming responses in manageable chunks.

### Iterators

- **`AsyncRequestIterator`**: Manages multiple asynchronous requests using async iterators.

### Coroutines & Async Iterators

- **Async Functions**: Handles client requests asynchronously.

### Inheritance and Polymorphism

- **`BaseRequestHandler`**: Abstract base class defining the structure for handling different types of HTTP requests.
- **`GetRequestHandler` and `PostRequestHandler`**: Concrete implementations for handling GET and POST requests, showcasing polymorphic behavior.

### Context Managers

- **`ServerContextManager`**: Ensures proper initialization and cleanup of server resources using async context managers.

### Singleton Pattern

- **`ServerContextManager`**: Implemented as a singleton to maintain a single instance of the server.

### Streaming Responses

- Implemented using the `stream_data` generator, allowing large responses to be sent incrementally to clients.

## How to Run

First, run the webserver.py file to instantiate a server connection,
Afterwards, split the terminal in 2 and run the client.py file. The client file will simulate requests to send to the server which in turn will gain responses from


https://github.com/user-attachments/assets/4e9f0f95-6a3f-499f-b1e8-6c71fbb15b4c

The unit test:


https://github.com/user-attachments/assets/c11d290e-1a99-4aac-8897-50963f6d232c

