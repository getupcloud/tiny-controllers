import os
import glob
from flask import Flask

METRICS_DATA_DIR = os.environ.get('METRICS_DATA_DIR', '/data/metrics')
METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))

app = Flask(__name__)

def read_prom(path):
    try:
        with open(path, 'r') as f:
            return f.read(), 200
    except FileNotFoundError:
        return '', 404

@app.route("/metrics/<app>")
def metrics_app(app):
    prom_file = f'{METRICS_DATA_DIR}/{app}.prom'
    return read_prom(prom_file)

@app.route("/metrics")
def metrics():
    def generate():
        for path in glob.glob(f'{METRICS_DATA_DIR}/*.prom'):
            data, _ = read_prom(path)
            yield data
    return generate(), {"Content-Type": "text/plain"}

app.run(host='0.0.0.0', port=METRICS_PORT)

