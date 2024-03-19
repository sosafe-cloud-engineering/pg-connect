import psycopg2
import boto3
import os
import http.server
import socketserver
import json

WEB_PORT = int(os.environ.get("WEB_PORT", "8000"))
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_NAME = os.environ.get("DB_NAME", "postgres")
REGION = os.environ.get("REGION", "eu-central-1")

session = boto3.Session(region_name=REGION)
client = session.client('rds')

def get_auth_data():
    """
    Get the username and password from the environment variable
    """
    return json.loads(os.environ.get("DB_PASSWORD"))

auth_data = get_auth_data()
conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", 5432),
    database=os.environ.get("DB_NAME", "postgres"),
    user=auth_data["username"],
    password=auth_data["password"],
)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            info = cur.fetchone()

        self.wfile.write(json.dumps({
            "version": info[0],
        }).encode("utf-8"))

try:
    with socketserver.TCPServer(("", WEB_PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server...")
    httpd.shutdown()
    conn.close()
    print("Server shut down successfully.")
