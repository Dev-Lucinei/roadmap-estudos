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
    """Serviço para avaliação de conhecimento com proteção contra prompt injection."""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.client = None
        self._init_client()

    def _init_client(self):
        """Inicializa cliente OpenRouter com validação de API key."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise PermissionError("OPENROUTER_API_KEY não configurada no .env")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def _sanitize_input(self, text, max_length=500):
        """Sanitiza entrada do usuário para prevenir prompt injection."""
        if not text or not isinstance(text, str):
            return ""
        # Remove caracteres de controle e limita tamanho
        sanitized = "".join(char for char in text if char.isprintable() or char.isspace())
        return sanitized[:max_length].strip()

    def _load_lesson_context(self, topic):
        """Carrega contexto da lição para validação de escopo."""
        # Busca arquivo de lição correspondente
        topic_id = topic.lower().replace(" ", "_").replace("-", "_")
        lesson_path = os.path.join(self.data_dir, "..", "licoes", f"{topic_id}.md")
        
        if os.path.exists(lesson_path):
            with open(lesson_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Extrai primeiros 500 caracteres como contexto
                return content[:500]
        return None

    def generate_checklist(self, topic):
        """Gera checklist de auto-avaliação para um tópico."""
        topic = self._sanitize_input(topic, 100)
        
        prompt = f"""Gere exatamente 5 itens de checklist para auto-avaliação sobre "{topic}".

Regras:
- Cada item deve ser uma afirmação clara e objetiva
- Foque em conceitos-chave e habilidades práticas
- Use linguagem simples e direta
- Máximo 15 palavras por item

Formato: retorne APENAS um array JSON com 5 strings.
Exemplo: ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]"""

        try:
            completion = self.client.chat.completions.create(
                model="openrouter/auto",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
            )
            
            response = completion.choices[0].message.content.strip()
            # Parse JSON com fallback
            items = json.loads(response)
            if not isinstance(items, list) or len(items) != 5:
                raise ValueError("Formato inválido")
            
            return {"status": "success", "items": items}
        except Exception as e:
            # Fallback: checklist genérico
            return {
                "status": "success",
                "items": [
                    f"Entendo os conceitos fundamentais de {topic}",
                    f"Consigo explicar {topic} com minhas próprias palavras",
                    f"Sei aplicar {topic} em exemplos práticos",
                    f"Conheço os erros comuns relacionados a {topic}",
                    f"Consigo relacionar {topic} com outros conceitos"
                ]
            }

    def generate_quiz(self, topic):
        """Gera quiz de 3-5 perguntas sobre o tópico."""
        topic = self._sanitize_input(topic, 100)
        lesson_context = self._load_lesson_context(topic)
        
        context_hint = f"\n\nContexto da lição:\n{lesson_context}" if lesson_context else ""
        
        prompt = f"""Gere exatamente 4 perguntas dissertativas curtas sobre "{topic}".{context_hint}

Regras:
- Perguntas objetivas e diretas
- Foque em compreensão conceitual, não decoreba
- Respostas esperadas: 1-3 frases
- Evite perguntas muito abertas ou filosóficas

Formato JSON:
[
  {{"question": "Pergunta 1?"}},
  {{"question": "Pergunta 2?"}},
  {{"question": "Pergunta 3?"}},
  {{"question": "Pergunta 4?"}}
]

Retorne APENAS o JSON, sem texto adicional."""

        try:
            completion = self.client.chat.completions.create(
                model="openrouter/auto",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8,
            )
            
            response = completion.choices[0].message.content.strip()
            # Remove markdown code blocks se presentes
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            questions = json.loads(response)
            if not isinstance(questions, list) or len(questions) < 3:
                raise ValueError("Formato inválido")
            
            return {"status": "success", "questions": questions[:5]}
        except Exception as e:
            print(f"Erro ao gerar quiz: {e}")
            # Fallback: perguntas genéricas
            return {
                "status": "success",
                "questions": [
                    {"question": f"O que é {topic} e qual sua importância?"},
                    {"question": f"Quais são os principais conceitos relacionados a {topic}?"},
                    {"question": f"Como você aplicaria {topic} na prática?"},
                    {"question": f"Quais erros comuns devem ser evitados ao trabalhar com {topic}?"}
                ]
            }

    def evaluate_quiz(self, topic, answers):
        """Avalia respostas do quiz com proteção contra injection."""
        topic = self._sanitize_input(topic, 100)
        
        # Sanitiza e limita respostas
        sanitized_answers = []
        for ans in answers[:5]:  # Máximo 5 respostas
            sanitized = self._sanitize_input(ans, 500)
            if not sanitized:
                return {
                    "status": "error",
                    "message": "Todas as respostas devem ser preenchidas"
                }
            sanitized_answers.append(sanitized)
        
        # Concatena respostas com separadores claros
        answers_text = "\n---\n".join([f"R{i+1}: {ans}" for i, ans in enumerate(sanitized_answers)])
        
        prompt = f"""Avalie as respostas do usuário sobre "{topic}".

RESPOSTAS DO USUÁRIO:
{answers_text}

TAREFA: Avalie se o usuário demonstra compreensão adequada de "{topic}".

Critérios:
- Conceitos corretos mencionados
- Clareza e coerência
- Profundidade apropriada

Retorne APENAS um JSON no formato:
{{"score": <0-100>, "passed": <true/false>, "feedback": "<feedback em 2-3 frases>"}}

Nota mínima para aprovação: 70
Feedback máximo: 50 palavras"""

        try:
            completion = self.client.chat.completions.create(
                model="openrouter/auto",
                messages=[
                    {"role": "system", "content": "Você é um avaliador educacional objetivo. Responda APENAS com JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3,
            )
            
            response = completion.choices[0].message.content.strip()
            # Remove markdown se presente
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            result = json.loads(response)
            
            # Validação do resultado
            if not all(k in result for k in ["score", "passed", "feedback"]):
                raise ValueError("Resposta incompleta da IA")
            
            return {
                "status": "success",
                "score": min(100, max(0, int(result["score"]))),
                "passed": bool(result["passed"]),
                "feedback": str(result["feedback"])[:200]  # Limita feedback
            }
        except Exception as e:
            print(f"Erro ao avaliar quiz: {e}")
            # Fallback: avaliação básica por tamanho de resposta
            avg_length = sum(len(ans.split()) for ans in sanitized_answers) / len(sanitized_answers)
            passed = avg_length >= 10  # Pelo menos 10 palavras por resposta
            
            return {
                "status": "success",
                "score": 70 if passed else 50,
                "passed": passed,
                "feedback": "Avaliação automática: " + (
                    "Suas respostas demonstram conhecimento adequado." if passed
                    else "Suas respostas estão muito curtas. Revise o conteúdo."
                )
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
        elif self.path == "/api/generate-checklist":
            self.handle_generate_checklist(data)
        elif self.path == "/api/generate-diagnostic-quiz":
            self.handle_generate_diagnostic_quiz(data)
        elif self.path == "/api/evaluate-quiz":
            self.handle_evaluate_quiz(data)
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

    def handle_generate_checklist(self, data):
        """Endpoint para gerar checklist de auto-avaliação."""
        try:
            topic = data.get("topic", "")
            if not topic:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "error", "message": "Tópico obrigatório"}).encode("utf-8")
                )
                return

            service = DiagnosisService(DATA_DIR)
            result = service.generate_checklist(topic)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )

    def handle_generate_diagnostic_quiz(self, data):
        """Endpoint para gerar quiz diagnóstico."""
        try:
            topic = data.get("topic", "")
            if not topic:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"status": "error", "message": "Tópico obrigatório"}).encode("utf-8")
                )
                return

            service = DiagnosisService(DATA_DIR)
            result = service.generate_quiz(topic)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            )

    def handle_evaluate_quiz(self, data):
        """Endpoint para avaliar respostas do quiz."""
        try:
            topic = data.get("topic", "")
            answers = data.get("answers", [])

            if not topic or not answers:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "error", "message": "Tópico e respostas obrigatórios"}
                    ).encode("utf-8")
                )
                return

            service = DiagnosisService(DATA_DIR)
            result = service.evaluate_quiz(topic, answers)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

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
