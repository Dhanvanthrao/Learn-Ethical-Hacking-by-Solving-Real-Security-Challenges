import docker
from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize the Docker client
client = docker.from_env()

# Define a function to retrieve container information

def get_container_info(container):
    try:
        # Get the container's IP address
        container_ip = container.attrs['NetworkSettings']['IPAddress']

        # Get the container's port information
        ports = container.attrs['NetworkSettings']['Ports']
        port_info = ""
        if ports:
            for port, mapping in ports.items():
                if mapping is not None:
                    if 'Proto' in mapping[0]:
                        port_info += f"{port}/{mapping[0]['Proto']} ({mapping[0]['HostIp']}:{mapping[0]['HostPort']}), "
                    else:
                        port_info += f"{port} (not mapped), "
            port_info = port_info[:-2] # Remove the last comma and space

        # Get the container's image name
        info = {}
        tags = container.image.tags
        if tags:
            info['image'] = tags[0]
        else:
            info['image'] = "Unknown"

        # Get the container's status
        is_running = container.status == 'running'
        info['is_running'] = is_running

    except docker.errors.APIError:
        # Handle case where container API throws an error
        container_ip = "Unknown"
        port_info = "No port"
        info = {}
        info['image'] = "Unknown"

    return container_ip, port_info, info

# Define a function to start a container and return success message
def start_container(container_id):
    container = client.containers.get(container_id)
    container.start()
    container_ip, port_info, image_info = get_container_info(container)
    status = "running" if container.status == "running" else "unknown"
    return f"Container {container_id} started successfully. Status: {status}"

# Define a function to stop a container and return success message
def stop_container(container_id):
    container = client.containers.get(container_id)
    container.stop()
    return f"Container {container_id} stopped successfully"

# Define a function to restart a container and return success message
def restart_container(container_id):
    container = client.containers.get(container_id)
    container.restart()
    container_ip, port_info, port_number, image_info = get_container_info(container)
    status = "running" if container.status == "running" else "unknown"
    return f"Container {container_id} restarted successfully. Status: {status}"

@app.before_request
def before_request():
    if request.path == '/start':
        container_id = request.form['container_id']
        message = start_container(container_id)
        print(message)
    elif request.path == '/stop':
        container_id = request.form['container_id']
        message = stop_container(container_id)
        print(message)
    elif request.path == '/restart':
        container_id = request.form['container_id']
        message = restart_container(container_id)
        print(message)

@app.route('/')
def home():
    # Get a list of all containers in my host machine.
    containers = client.containers.list(all=True)

    # Get information for each container
    container_info = []
    for container in containers:
        info = {}
        info['id'] = container.id
        info['name'] = container.name
        container_ip, port_info, image_info = get_container_info(container)
        info.update({'ip': container_ip, 'ports': port_info})
        info.update(image_info)
        info['status'] = container.status
        container_info.append(info)

    # Render the template with the container information
    return render_template('index.html', container_info=container_info)

    
@app.route('/start', methods=['POST'])
def start():
    container_id = request.form['container_id']
    start_container(container_id)
    return 'success'

@app.route('/stop', methods=['POST'])
def stop():
    container_id = request.form['container_id']
    stop_container(container_id)
    return 'success'

@app.route('/restart', methods=['POST'])
def restart():
    container_id = request.form['container_id']
    restart_container(container_id)
    return 'success'

if __name__ == '__main__':
    app.run()