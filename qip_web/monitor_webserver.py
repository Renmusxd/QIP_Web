from qip_web.monitor_server import MonitorServer
from flask import Flask, render_template

app = Flask(__name__)
monitor_server = None


@app.route('/api', methods=['GET'])
def api():
    pass


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    monitor_server = MonitorServer()
    app.run('0.0.0.0', 8080, debug=True)
