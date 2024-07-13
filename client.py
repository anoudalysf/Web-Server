import socket
import json

HOST, PORT = "localhost", 8000

# json data to send in the post request
json_data_post = {
    "name": "Jane Doe",
    "age": 25,
    "city": "New York"
}

# json data for the get request (empty for illustration)
json_data_get = {}

# convert json data to string for post request
data_post = json.dumps(json_data_post)
auth_token = 'my_secret_token'

# to test if auth works switch the token to this vv incorrect token
# auth_token = 'no'

# convert json data to string for get request
data_get = json.dumps(json_data_get)

def send_request(method, data=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        
        if method == 'GET':
            request = f"GET / HTTP/1.1\n" \
                      f"Content-Type: application/json\n" \
                      f"Authorization: {auth_token}\n\n"
            
        elif method == 'POST':
            request = f"POST / HTTP/1.1\n" \
                      f"Content-Type: application/json\n" \
                      f"Content-Length: {len(data)}\n" \
                      f"Authorization: {auth_token}\n\n" \
                      f"{data}"
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # send request
        sock.sendall(request.encode())
        
        # receive data from the server until the connection is closed
        received = ""
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            received += chunk.decode()
    
    return received


if __name__ == "__main__":
    print("Simulating GET request...")
    response_get = send_request('GET', data_get)
    print("Received response for GET request:")
    print(response_get)
    
    print("\nSimulating POST request with correct data...")
    response_post = send_request('POST', data_post)
    print("Sent POST request with data:")
    print(data_post)
    print("Received response for POST request:")
    print(response_post)
    
    # simulate a post request with incorrect data (ex: missing 'name' field)
    json_data_post_incorrect = {
        "age": 25,
        "city": "New York"
    }
    data_post_incorrect = json.dumps(json_data_post_incorrect)
    
    print("\nSimulating POST request with incorrect data...")
    response_post_incorrect = send_request('POST', data_post_incorrect)
    print("Sent POST request with incorrect data:")
    print(data_post_incorrect)
    print("Received response for POST request with incorrect data:")
    print(response_post_incorrect)
