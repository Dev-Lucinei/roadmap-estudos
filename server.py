import http.server
import socketserver
import json
import os
import sys
import urllib.parse

# Adiciona o diretório atual ao path para permitir importações locais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from generate_lessons import processar_node
from generate_roadmap import gerar_roadmap_ia, salvar_roadmap

PORT = 8000
DATA_DIR = os.path.join(BASE_DIR, "data")
LICOES_DIR = os.path.join(BASE_DIR, "licoes")

class RoadmapHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/roadmaps':
            self.list_roadmaps()
        elif self.path.startswith('/api/roadmap/'):
            self.load_roadmap()
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/api/generate-lesson':
            self.handle_generate_lesson(data)
        elif self.path == '/api/generate-roadmap':
            self.handle_generate_roadmap(data)
        elif self.path == '/api/save-roadmap':
            self.handle_save_roadmap(data)
        else:
            self.send_error(404)

    def do_DELETE(self):
        self.send_response(200)
        self.end_headers()

    def list_roadmaps(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(files).encode('utf-8'))

    def load_roadmap(self):
        filename = self.path.split('/')[-1]
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404)

    def handle_generate_lesson(self, data):
        try:
            node_id = data['id']
            title = data['title']
            node_type = data.get('type', 'subtopic')
            filepath = processar_node(node_id, title, node_type)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "file": filepath}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def handle_generate_roadmap(self, data):
        try:
            tema = data['tema']
            roadmap_dados = gerar_roadmap_ia(tema)
            if roadmap_dados:
                filepath = salvar_roadmap(tema, roadmap_dados)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "file": os.path.basename(filepath)}).encode('utf-8'))
            else:
                raise Exception("Falha na geração pela IA")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def handle_save_roadmap(self, data):
        try:
            filename = data['filename']
            roadmap_dados = data['data']
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(roadmap_dados, f, indent=4, ensure_ascii=False)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), RoadmapHandler) as httpd:
    print(f"🚀 Roadmap Server rodando em http://localhost:{PORT}")
    httpd.serve_forever()
