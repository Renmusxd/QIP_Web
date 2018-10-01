from qip_web.monitor_server import MonitorServer
from flask import Flask, render_template, jsonify, send_from_directory, redirect


app = Flask(__name__)
monitor_server = None


@app.before_first_request
def activate_job():
    global monitor_server
    print("[*] Starting server...")
    monitor_server = MonitorServer()
    monitor_server.start()


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/api/jobs', methods=['GET'])
def job_list():
    return jsonify(monitor_server.list_jobs())


@app.route('/api/jobs/<job>', methods=['GET'])
def json_job(job):
    job_details = monitor_server.job_details(job)
    return jsonify(job_details)


@app.route('/jobs/<job>')
def job_page(job):
    job_details = monitor_server.job_details(job)
    return render_template('job.html', job=job, n_qubits=job_details['n'],
                           workers=job_details['workers'])


@app.route('/job')
def first_job_page():
    jobs = monitor_server.list_jobs()
    if len(jobs) > 0:
        return redirect('/jobs/' + jobs[0])
    else:
        return redirect('/')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', jobs=monitor_server.list_jobs())


if __name__ == "__main__":
    app.run('0.0.0.0', 8080, debug=True)
