import os
from http.server import HTTPServer, CGIHTTPRequestHandler
from multiprocessing import Process

def run_server(port):
    # Make sure the server is pointed towards the correct directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.chdir("../static/")
    # Create server object listening the port 3000
    REPL_interface = HTTPServer(server_address=('', port), RequestHandlerClass=CGIHTTPRequestHandler)
    # Start the web server
    REPL_interface.serve_forever()

if __name__ == "__main__":
    run_server(3000)
