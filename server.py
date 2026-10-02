import os
import sys
import json
import socket
import pandas as pd

SOCKET_PATH = "/tmp/rag_service.sock"

class RAGService:
    def __init__(self):
        self.corpus_dir = None
        self.indexed_files = []
        print("[*] Initializing RAG Service...")

    def index(self, corpus_dir):
        self.corpus_dir = corpus_dir
        self.indexed_files = []
        for root, _, files in os.walk(corpus_dir):
            for file in files:
                p = os.path.join(root, file)
                if os.access(p, os.R_OK):
                    self.indexed_files.append(p)
        print(f"[+] Service indexed {len(self.indexed_files)} files.")
        return {"status": "ok", "indexed_count": len(self.indexed_files)}

    def query(self, corpus_dir, query_text):
        answer = ""
        citations = []
        confidence = 0.0

        for file_path in self.indexed_files:
            rel_path = os.path.relpath(file_path, corpus_dir)
            try:
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                    for col in df.columns:
                        m = df[df[col].astype(str).str.contains(query_text, case=False, na=False)]
                        if not m.empty:
                            answer = str(m.iloc[0].values[1]) if len(m.iloc[0].values) > 1 else str(m.iloc[0].values[0])
                            citations = [rel_path]
                            confidence = 0.90
                            break
            except Exception:
                continue

            if answer:
                break

        return {
            "answer": answer.strip() if answer else "",
            "citations": citations,
            "confidence": confidence if answer else 0.0
        }

def start_server():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    service = RAGService()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    print(f"[+] Daemon listening on {SOCKET_PATH}")

    while True:
        conn, _ = server.accept()
        data = conn.recv(4096).decode('utf-8')
        if not data:
            conn.close()
            continue

        req = json.loads(data)
        action = req.get("action")

        if action == "index":
            resp = service.index(req.get("corpus_dir"))
        elif action == "query":
            resp = service.query(req.get("corpus_dir"), req.get("query_text"))
        else:
            resp = {"error": "unknown action"}

        conn.sendall(json.dumps(resp).encode('utf-8'))
        conn.close()

if __name__ == "__main__":
    start_server()
