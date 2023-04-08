import dask.distributed as dd
import smtplib
import time
from flask import Flask, render_template, request

# Define your email settings
email_address = 'your_email@example.com'
email_password = 'your_email_password'
recipient_email = 'recipient_email@example.com'

def send_email(subject, message):
    """Send an email using the given email address and password."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address, email_password)
    email_body = f'Subject: {subject}\n\n{message}'
    server.sendmail(email_address, recipient_email, email_body)
    server.quit()

# Define your Dask cluster
cluster = dd.LocalCluster(n_workers=4)

# Define your worker functions
def worker_function_1():
    while True:
        # Your long-running task
        time.sleep(1)

def worker_function_2():
    while True:
        # Your long-running task
        time.sleep(2)

# Submit your worker functions
client = dd.Client(cluster)
futures = [client.submit(worker_function_1), client.submit(worker_function_2)]

# Define your Flask web application
app = Flask(__name__)

@app.route('/')
def index():
    """Render the index page with the status of each future."""
    status = []
    for i, future in enumerate(futures):
        if future.done():
            try:
                future.result()
                status.append(f'Worker function {i} completed successfully.')
            except Exception as e:
                error_message = str(e)
                status.append(f'Error: {error_message}')
        else:
            status.append(f'Worker function {i} is running.')
    return render_template('index.html', status=status)

@app.route('/restart')
def restart():
    """Restart the specified future."""
    future_index = int(request.args.get('future'))
    futures[future_index] = client.submit([worker_function_1, worker_function_2][future_index])
    return 'Future restarted.'

@app.route('/kill')
def kill():
    """Kill the specified future."""
    future_index = int(request.args.get('future'))
    futures[future_index].cancel()
    return 'Future killed.'

# Start the Flask web application
if __name__ == '__main__':
    app.run(debug=True)
