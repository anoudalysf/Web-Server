import socket
import json
from abc import ABC, abstractmethod
from functools import wraps
import datetime
import asyncio

SERVER_HOST = "localhost"
SERVER_PORT = 8000
auth_token = 'my_secret_token'

class AuthorizationError(Exception):
    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)
        

# decorators
def log_request(func):
    @wraps(func)
    async def wrapper_log_request(*args, **kwargs):
        request_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request_data = kwargs.get('request_data', '')
        print(f'{args[1]} {request_time}:')
        print(request_data)
        return await func(*args, **kwargs)
    return wrapper_log_request

def authorize_request(func):
    @wraps(func)
    def wrapper_authorize_request(*args, **kwargs):
        headers = kwargs.get('headers', {})
        authorization_header = headers.get('Authorization', None)
        
        if authorization_header == auth_token:
            return func(*args, **kwargs)
        else:
            raise AuthorizationError('Unauthorized')
    
    return wrapper_authorize_request

# async iterator
class AsyncRequestIterator:
    def __init__(self):
        self.requests = [] 
        self.index = 0

    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index < len(self.requests):
            request_data = self.requests[self.index]
            self.index += 1
            return request_data
        else:
            raise StopAsyncIteration

    def add_request(self, request_data):
        self.requests.append(request_data)

    def clear_requests(self):
        self.requests = []
        self.index = 0


# inheritance and polymorphism
class BaseRequestHandler(ABC):
    @abstractmethod
    def handle_request(self, request_data):
        pass

class GetRequestHandler(BaseRequestHandler):
    @log_request
    async def handle_request(self, request_data):
        await asyncio.sleep(1)
        return 'HTTP/1.0 200 OK\n\nHello from GET request handler'

class PostRequestHandler(BaseRequestHandler):
    @log_request
    @authorize_request
    async def handle_request(self, request_data, headers):
        try:
            await asyncio.sleep(1)
            # extract json data from request_data
            json_start_index = request_data.find('{')
            if json_start_index != -1:
                json_data_str = request_data[json_start_index:]
                json_data = json.loads(json_data_str)
                
                # validate expected keys (if theres a typo or missign headers it will return an error)
                expected_keys = {"name", "age", "city"}
                received_keys = set(json_data.keys())
                
                if not expected_keys.issubset(received_keys):
                    return f'HTTP/1.0 400 Bad Request\n\nMissing required keys: {", ".join(expected_keys - received_keys)}'
                
                return f'HTTP/1.0 200 OK\n\nReceived POST data: {json_data}'
            else:
                return 'HTTP/1.0 400 Bad Request\n\nNo JSON data found'
        except json.JSONDecodeError as e:
            return f'HTTP/1.0 400 Bad Request\n\nError decoding JSON: {str(e)}'
        except Exception as e:
            return f'HTTP/1.0 500 Internal Server Error\n\n{str(e)}'


async def response_generator(response_code, data=None):
    if data:
        yield f'HTTP/1.0 {response_code}\nContent-Length: {len(data)}\n\n{data}'
    else:
        yield f'HTTP/1.0 {response_code} OK\n\n'

# handling the client responses
async def handle_client_request(client_reader, client_writer):
    try:
        request_data = await client_reader.read(1024)
        request = request_data.decode()
        headers, method, path, request_body = parse_request(request)
        async_request_iterator.add_request(request)
        
        if method == 'GET':
            handler = GetRequestHandler()
            response_data = await handler.handle_request(request_body)

        elif method == 'POST':
            handler = PostRequestHandler()
            response_data = await handler.handle_request(request_body, headers=headers)
        else:
            response_data = 'HTTP/1.0 405 Method Not Allowed\n\nUnsupported request method'
        
        print(f'{method} {path} HTTP/1.1')
        for header, value in headers.items():
            print(f'{header}: {value}')
        print()

        client_writer.write(response_data.encode())
        await client_writer.drain()
    
    except asyncio.TimeoutError:
        response_data = 'HTTP/1.0 408 Request Timeout\n\nTimeout waiting for client request.'
        client_writer.write(response_data.encode())
        await client_writer.drain()
    
    # when they dont have authorization (dont have the required key)
    except AuthorizationError:
        response_data = 'HTTP/1.0 401 Unauthorized\n\nAuthorization Required'
        client_writer.write(response_data.encode())
        await client_writer.drain()
    except Exception as e:
        response_data = f'HTTP/1.0 500 Internal Server Error\n\n{str(e)}'
        client_writer.write(response_data.encode())
        await client_writer.drain()
    finally:
        client_writer.close()

async_request_iterator = AsyncRequestIterator()

# parsing the request
def parse_request(request):
    headers = {}
    lines = request.split('\n')
    
    request_line = lines[0].strip().split(' ')
    method = request_line[0]  # the HTTP method (get post etc)
    path = request_line[1]    # requested path
    
    for line in lines[1:]:
        if not line.strip():
            break
        key, value = line.split(':', 1)
        headers[key.strip()] = value.strip()
    
    request_data = lines[-1]
    
    return headers, method, path, request_data

class ServerContextManager:
    _instance = None  # class variable to store the instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.server_socket = None  # initialize the server socket

    async def __aenter__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.server_socket.listen(1)
        print(f'Listening on port {SERVER_PORT} ...')
        return self.server_socket

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.server_socket:
            self.server_socket.close()
            print("Server socket closed.")

# testing singleton behavior
def test_singleton():
    instance1 = ServerContextManager()
    instance2 = ServerContextManager()

    assert instance1 is instance2, "Not the same"

    print("Singleton test passed.")

# main function to run the server
async def main():
    server = None
    try:
        server = await asyncio.start_server(handle_client_request, SERVER_HOST, SERVER_PORT)
        print(f'Listening on {SERVER_HOST}:{SERVER_PORT} ...')

        async with server:
            await server.serve_forever()
    finally:
        if server:
            server.close()
            await server.wait_closed()
        print("Server closed.")

# run the server
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer interrupted. Closing server...")
        pass

# run the singleton test
test_singleton()
