import http.server
import socketserver
import json
import os
import sys
from pathlib import Path

# Carrega variáveis do .env para não expor chaves no código
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

from openai import OpenAI  # noqa: E402

# Adiciona o diretório atual ao path para permitir importações locais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from generate_lessons import processar_node  # noqa: E402
from generate_roadmap import gerar_roadmap_ia, salvar_roadmap  # noqa: E402

PORT = 8000
DATA_DIR = os.path.join(BASE_DIR, "data")
LICOES_DIR = os.path.join(BASE_DIR, "licoes")


class DiagnosisService:
    """Serviço independente para processar diagnósticos de lacunas de conhecimento."""

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def diagnose(self, topic, user_answer):
        # Load dependency map
        dep_map_path = os.path.join(self.data_dir, "dep_map.json")
        if not os.path.exists(dep_map_path):
            raise FileNotFoundError("Mapa de dependências não encontrado")

        with open(dep_map_path, "r", encoding="utf-8") as f:
            dep_map = json.load(f)

        # Get prerequisites for the topic
        prerequisites = dep_map.get(topic, [])

        # Check if we have OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise PermissionError("API key não configurada")

        # Initialize OpenRouter client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        # Create prompt for diagnosis
        prompt = f"""
        Analise a seguinte resposta do usuário sobre o tópico "{topic}":
        "{user_answer}"
        
        Pré-requisitos para este tópico: {", ".join(prerequisites) if prerequisites else "Nenhum"}
        
        Forneça um diagnóstico conciso (máximo 100 palavras) que:
        1. Identifique se há lacunas de conhecimento nos pré-requisitos
        2. Se houver lacunas, explique qual pré-requisito está faltando e por que é importante
        3. Se não houver lacunas, confirme que o usuário pode avançar
        4. Inclua uma fórmula/regra relevante e um erro comum
        
        Responda APENAS com o diagnóstico, sem formatação extra.
        """

        # Call OpenRouter API
        completion = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )

        diagnosis = completion.choices[0].message.content.strip()

        # Ensure diagnosis is under 100 words
        words = diagnosis.split()
        if len(words) > 100:
            diagnosis = " ".join(words[:100]) + "..."

        # Determine if there's a knowledge gap
        gap_indicators = [
            "falta",
            "não sabe",
            "revisar",
            "precisa",
            "lacuna",
            "não entende",
        ]
        has_gap = any(indicator in diagnosis.lower() for indicator in gap_indicators)

        return {
            "status": "miss" if has_gap else "hit",
            "message": diagnosis,
            "tags": prerequisites,
            "has_gap": has_gap,
        }


class RoadmapHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS restrito à origem local — não expor para qualquer origem em produção
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/roadmaps":
            self.list_roadmaps()
        elif self.path.startswith("/api/roadmap/"):
            self.load_roadmap()
        elif self.path == "/api/dep-map":
            self.get_dep_map()
        else:
            super().do_GET()

    def do_POST(self):
        # P0: Validação de Content-Length antes de ler o body
        try:
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                self.send_response(411)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "error", "message": "Content-Length obrigatório"}
                    ).encode("utf-8")
                )
                return
            content_length = int(raw_length)
            if content_length > 1_048_576:  # limite de 1MB
                self.send_response(413)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "error", "message": "Payload muito grande"}
                    ).encode("utf-8")
                )
                return
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"status": "error", "message": f"Requisição inválida: {e}"}
                ).encode("utf-8")
            )
            return

        if self.path == "/api/generate-lesson":
            self.handle_generate_lesson(data)
        elif self.path == "/api/generate-roadmap":
            self.handle_generate_roadmap(data)
        elif self.path == "/api/save-roadmap":
            self.handle_save_roadmap(data)
        elif self.path == "/api/diagnose":
            self.handle_diagnosis(data)
        elif self.path == "/api/regenerate-dep-map":
            self.handle_regenerate_dep_map()
        else:
            self.send_error(404)

    def do_DELETE(self):
        # Endpoint de DELETE não possui lógica implementada — retorna 405
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "error", "message": "Método não suportado"}).encode(
                "utf-8"
            )
        )

    def list_roadmaps(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        EXCLUDED = {"dep_map.json"}
        files = [
            f for f in os.listdir(DATA_DIR) if f.endswith(".json") and f not in EXCLUDED
        ]
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(files).encode("utf-8"))

    def load_roadmap(self):
        # P0: Sanitização de path para prevenir path traversal
        raw_name = self.path.split("/")[-1]
        filename = os.path.basename(raw_name)
        filepath = os.path.realpath(os.path.join(DATA_DIR, filename))
        # Garante que o caminho resolvido está dentro de DATA_DIR
        if not filepath.startswith(os.path.realpath(DATA_DIR) + os.sep):
            self.send_error(403)
            return
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_error(404)

    def get_dep_map(self):
        filepath = os.path.join(DATA_DIR, "dep_map.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"status": "error", "message": "dep_map.json não encontrado"}
                ).encode("utf-8")
            )

    def handle_generate_lesson(self, data):
        try:
            node_id = data["id"]
            title = data["title"]
            node_type = data.get("type", "subtopic")
            filepath = processar_node(node_id, title, node_type)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "success", "file": filepath}).encode("utf-8")
            )
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )

    def handle_generate_roadmap(self, data):
        try:
            tema = data["tema"]
            roadmap_dados = gerar_roadmap_ia(tema)
            if roadmap_dados:
                filepath = salvar_roadmap(tema, roadmap_dados)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "success", "file": os.path.basename(filepath)}
                    ).encode("utf-8")
                )
            else:
                raise Exception("Falha na geração pela IA")
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )

    def handle_save_roadmap(self, data):
        try:
            # P0: Sanitização de filename para prevenir path traversal
            raw_name = data.get("filename", "")
            filename = os.path.basename(raw_name)
            if not filename.endswith(".json") or not filename:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "error", "message": "Nome de arquivo inválido"}
                    ).encode("utf-8")
                )
                return
            roadmap_dados = data["data"]
            filepath = os.path.realpath(os.path.join(DATA_DIR, filename))
            if not filepath.startswith(os.path.realpath(DATA_DIR) + os.sep):
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "error", "message": "Acesso negado"}).encode(
                        "utf-8"
                    )
                )
                return
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(roadmap_dados, f, indent=4, ensure_ascii=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )

    def handle_diagnosis(self, data):
        try:
            topic = data.get("topic", "")
            user_answer = data.get("user_answer", "")

            if not topic or not user_answer:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "status": "error",
                            "message": "Tópico e resposta são obrigatórios",
                        }
                    ).encode("utf-8")
                )
                return

            # Use the DiagnosisService
            service = DiagnosisService(DATA_DIR)
            result = service.diagnose(topic, user_answer)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except FileNotFoundError as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )
        except PermissionError as e:
            # API key missing - configuration error, return 500
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )
        except Exception as e:
            # Check if it's an OpenAI-related error (LLM failure) - return 502
            error_msg = str(e).lower()
            if "openai" in error_msg or "api" in error_msg or "llm" in error_msg:
                self.send_response(502)
            else:
                self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"status": "error", "message": f"Erro no diagnóstico: {str(e)}"}
                ).encode("utf-8")
            )

    def handle_regenerate_dep_map(self):
        try:
            import glob

            dep_map = {}
            roadmap_files = glob.glob(os.path.join(DATA_DIR, "roadmap_*.json"))

            for filepath in roadmap_files:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                title = data.get(
                    "title",
                    os.path.basename(filepath)
                    .replace("roadmap_", "")
                    .replace(".json", ""),
                )
                nodes = data.get("nodes", [])

                prereqs = []
                for node in nodes:
                    if node.get("type") == "subtopic" and node.get("children"):
                        prereqs.extend(node["children"])

                dep_map[title] = list(set(prereqs))

            dep_map_path = os.path.join(DATA_DIR, "dep_map.json")
            with open(dep_map_path, "w", encoding="utf-8") as f:
                json.dump(dep_map, f, indent=2, ensure_ascii=False)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "status": "success",
                        "message": "dep_map.json atualizado",
                        "entries": len(dep_map),
                    }
                ).encode("utf-8")
            )
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RoadmapHandler) as httpd:
        print(f"🚀 Roadmap Server rodando em http://localhost:{PORT}")
        httpd.serve_forever()
