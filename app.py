import argparse
import json
import os
import socket
import sys

SOCKET_PATH = "/tmp/rag_service.sock"

def send_request(payload):
    if not os.path.exists(SOCKET_PATH):
        print(f"[!] Socket {SOCKET_PATH} not found. Is server.py running?", file=sys.stderr)
        sys.exit(1)
        
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(json.dumps(payload).encode('utf-8'))
    
    response = client.recv(4096).decode('utf-8')
    client.close()
    return json.loads(response)

def main():
    parser = argparse.ArgumentParser(description="AMD Thin Client")
    parser.add_argument("--index", type=str, help="Corpus to index")
    parser.add_argument("--corpus", type=str, help="Corpus directory")
    parser.add_argument("--query-id", type=str, help="Query ID")
    parser.add_argument("--query", type=str, help="Query text")

    args = parser.parse_args()

    if args.index:
        res = send_request({"action": "index", "corpus_dir": args.index})
        print(f"[+] Index response: {res}")
    elif args.corpus and args.query_id and args.query:
        res = send_request({
            "action": "query",
            "corpus_dir": args.corpus,
            "query_text": args.query
        })
        
        out_dir = "/app/output" if os.path.exists("/app") else "output"
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{args.query_id}_output.json")
        
        with open(out_file, "w") as f:
            json.dump(res, f, indent=2)
            
        print(f"[+] Output written to {out_file}")
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
