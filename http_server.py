import re
import socket
import threading


class HTTPServer:
    def __init__(self, host, port, paths):
        self.host = host
        self.port = port
        self.paths = paths
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def match_path(self, path):
        for compiled_path in self.paths:
            if '<' in compiled_path:
                if re.match(compiled_path.split('<')[0], path):
                    # "/account/" ::: "/account/lea"
                    # return "/account/<username>"
                    return compiled_path
            else:
                if path == compiled_path:
                    return compiled_path
        return None

    def handle_request(self, client_connection):
        request = client_connection.recv(1024)
        decoded_request = request.decode('utf-8')

        # Extract the HTTP method and path from the request
        method, path, _ = decoded_request.split(' ', 2)

        # Match the path against the compiled paths dictionary
        matched_path = self.match_path(path)

        # Serve the file corresponding to the matched path
        if matched_path is not None:
            param_name = ""
            # If the matched path is a dynamic path, extract the parameter value
            if '<' in matched_path:
                param_name = matched_path.split('<')[1].split('>')[0]
                # path = "/account/lea"    ["","account","lea"]
                # param_value = "lea"
                param_value = path.split('/')[-1]
                file_path = self.paths[matched_path]#.replace(f'<{param_name}>', param_value)
            else:
                file_path = self.paths[matched_path]
            

            # "<" + param_name + ">" to bytes  // param_name for exmaple "username"
            param_before = bytes(f"<{param_name}>",'utf-8')

            # Open the file, read its contents, and replace the <username> placeholder if it exists
            with open(file_path, 'rb') as f:
                file_content = f.read()
                if param_before in file_content:
                    file_content = file_content.replace(param_before, param_value.encode('utf-8'))
            

            # Send the response headers and file content back to the client
            response = b'HTTP/1.0 200 OK\n\n' + file_content
            client_connection.sendall(response)
        else:
            # If the path isn't found, send a 404 Not Found response
            with open('404.html', 'rb') as f:
                file_content = f.read()
            response = b'HTTP/1.0 404 Not Found\n\n' + file_content
            client_connection.sendall(response)

        client_connection.close()

    def run_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on http://{self.host}:{self.port}")

        while True:
            client_connection, client_address = self.server_socket.accept()
            print(f"New client connected: {client_address}")
            client_handler = threading.Thread(target=self.handle_request, args=(client_connection,))
            client_handler.start()
