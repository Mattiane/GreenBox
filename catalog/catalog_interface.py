import json
import uuid
from pathlib import Path
from os import path

P = Path(__file__).parent.absolute()
CONFIG_FILE = P / 'config.json'
USERS_FILE = P / 'users.json'
SESSIONS_FILE = P / 'sessions.json'
SERVICES_FILE = P / 'services.json'
RESOURCES_FILE = P / 'resources.json'
GREENHOUSES_FILE = P / 'generator' / 'greenhouses.json'
DEVICES_FILE = P / 'generator' / 'devices.json'


def init():
    catalogs = [USERS_FILE, SESSIONS_FILE, SERVICES_FILE, RESOURCES_FILE]
    for catalog in catalogs:
        if not path.exists(catalog):
            with open(catalog, 'w') as f:
                f.write(json.dumps({}))


def retrieve_broker():
    """
    Used to retrieve ip and port of the broker
    """
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
        broker_ip = data['broker_ip']
        broker_port = data['broker_port']
    return broker_ip, broker_port


def signup_user(username, password):
    """
    Used to register a new user into the system.
    """
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if username in users:
        return False
    users[username] = {
        'password': password,
        'greenhouses': []
    }
    with open(USERS_FILE, 'w') as f:
        f.write(json.dumps(users))
    return True


def validate_login(username, password):
    """
    Used to validate login credentials and give a session token to the
    user.
    """
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if username not in users:
        return None
    if not users[username]['password'] == password:
        return None
    return _generate_token(username)


def _generate_token(username):
    """
    Used to generate an unique session token for the given user. This
    token is assumed unique, under the assumption that UUID4 is an
    unique identifier.
    """
    token = str(uuid.uuid4())
    clean_sessions = _expire_token(username)
    clean_sessions[token] = {'username': username}
    with open(SESSIONS_FILE, 'w') as f:
        f.write(json.dumps(clean_sessions))
    return token


def _expire_token(username):
    """
    Used to delete the active token for a given user.
    """
    with open(SESSIONS_FILE, 'r') as f:
        sessions = json.load(f)
    clean_sessions = {k: v for k, v in sessions.items() if v['username'] != username}
    return clean_sessions


def verify_token(token):
    """
    Used to verify the validity of a specific session token.
    """
    if token is None:
        return False
    with open(SESSIONS_FILE, 'r') as f:
        sessions = json.load(f)
        if token in sessions:
            return True
    return False


def retrieve_username_by_token(token):
    """
    Used to retrieve the username given a specific session token.
    """
    with open(SESSIONS_FILE, 'r') as f:
        sessions = json.load(f)
    if token in sessions:
        return sessions[token]['username']
    return None


def verify_greenhouse_existence(greenhouse_id):
    """
    Used to verify that a specified greenhouse is registered. This is
    to prevent that an user can claim a greenhouse that is not registered.
    """
    with open(GREENHOUSES_FILE, 'r') as f:
        greenhouses = json.load(f)
    if greenhouse_id in greenhouses:
        return True
    return False


def verify_device_existence(device_id):
    """
    Used to verify that a specified device is registered. This is
    to prevent that an user can associate a device that is not registered.
    """
    with open(DEVICES_FILE, 'r') as f:
        devices = json.load(f)
    if device_id in devices:
        return True
    return False


def verify_greenhouse_ownership(greenhouse_id, username):
    """
    Used to verify if the user owns a specific greenhouse.
    """
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if greenhouse_id in users[username]['greenhouses']:
        return True
    return False


def retrieve_greenhouses(username):
    """
    Used to retrieve all the greenhouses owned by the given user.
    """
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    return users[username]['greenhouses']


def associate_greenhouse(greenhouse_id, greenhouse_name, username):
    """
    Used to associate a greenhouse to a user.
    """
    # Updating user's catalog
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    users[username]['greenhouses'].append(greenhouse_id)
    with open(USERS_FILE, 'w') as f:
        f.write(json.dumps(users))
    # Updating resource's catalog
    with open(RESOURCES_FILE, 'r') as f:
        resources = json.load(f)
    resources[greenhouse_id] = []
    with open(RESOURCES_FILE, 'w') as f:
        f.write(json.dumps(resources))
    # Updating greenhouses' catalog
    with open(GREENHOUSES_FILE, 'r') as f:
        greenhouses = json.load(f)
    greenhouses[greenhouse_id]['owner'] = username
    greenhouses[greenhouse_id]['name'] = greenhouse_name
    with open(GREENHOUSES_FILE, 'w') as f:
        f.write(json.dumps(greenhouses))


def retrieve_devices(greenhouse_id):
    """
    Used to retrieve all the devices registered under the given
    greenhouse.
    """
    with open(RESOURCES_FILE, 'r') as f:
        greenhouses = json.load(f)
    if greenhouse_id in greenhouses:
        return greenhouses[greenhouse_id]
    return None


if __name__ == '__main__':
    init()
