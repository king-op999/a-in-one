from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, Response
import requests
import json
import time
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== DATA STORAGE ====================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_json(filename, default=None):
    if default is None:
        default = {}
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return default

def save_json(filename, data):
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ==================== INITIALIZE DATA ====================
def init_data():
    # Users
    if not (DATA_DIR / "users.json").exists():
        save_json("users.json", {
            "admin": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "role": "admin"
            }
        })
    
    # API Keys
    if not (DATA_DIR / "keys.json").exists():
        save_json("keys.json", {
            "demo": {
                "key": "demo",
                "type": "FREE",
                "expires": str(datetime.now() + timedelta(days=4)),
                "daily_limit": 1000,
                "per_minute_limit": 80,
                "requests_today": 0,
                "last_reset": datetime.now().strftime("%Y-%m-%d"),
                "minute_requests": [],
                "status": "active",
                "created": str(datetime.now()),
                "created_by": "system"
            },
            "admin-op": {
                "key": "admin-op",
                "type": "ADMIN",
                "expires": "unlimited",
                "daily_limit": float('inf'),
                "per_minute_limit": float('inf'),
                "requests_today": 0,
                "last_reset": datetime.now().strftime("%Y-%m-%d"),
                "minute_requests": [],
                "status": "active",
                "created": str(datetime.now()),
                "created_by": "system"
            },
            "ft-op": {
                "key": "ft-op",
                "type": "OWNER",
                "expires": "unlimited",
                "daily_limit": float('inf'),
                "per_minute_limit": float('inf'),
                "requests_today": 0,
                "last_reset": datetime.now().strftime("%Y-%m-%d"),
                "minute_requests": [],
                "status": "active",
                "created": str(datetime.now()),
                "created_by": "system"
            }
        })
    
    # APIs
    if not (DATA_DIR / "apis.json").exists():
        save_json("apis.json", {
            "rc": {
                "name": "RC Info",
                "url": "https://simple-rc-info.vercel.app/rc",
                "params": {"num": "{param}"},
                "method": "GET",
                "timeout": 30,
                "status": "active",
                "added_by": "system",
                "created": str(datetime.now())
            }
        })

init_data()

# ==================== DECORATORS ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def check_api_key():
    api_key = request.args.get('key', '') or request.headers.get('X-API-Key', '')
    
    if not api_key:
        return False, "API key required", None
    
    keys = load_json("keys.json")
    
    if api_key not in keys:
        return False, "Invalid API key", None
    
    key_data = keys[api_key]
    
    if key_data.get("status") != "active":
        return False, "API key inactive", None
    
    if key_data["expires"] != "unlimited":
        try:
            expiry = datetime.fromisoformat(key_data["expires"])
            if datetime.now() > expiry:
                return False, "API key expired", None
        except:
            pass
    
    today = datetime.now().strftime("%Y-%m-%d")
    if key_data.get("last_reset") != today:
        key_data["requests_today"] = 0
        key_data["last_reset"] = today
        key_data["minute_requests"] = []
    
    daily_limit = key_data.get("daily_limit", float('inf'))
    if isinstance(daily_limit, str):
        daily_limit = float('inf') if daily_limit == 'inf' else int(daily_limit)
    
    if key_data.get("requests_today", 0) >= daily_limit:
        return False, f"Daily limit reached ({daily_limit} requests/day)", None
    
    per_minute = key_data.get("per_minute_limit", float('inf'))
    if isinstance(per_minute, str):
        per_minute = float('inf') if per_minute == 'inf' else int(per_minute)
    
    current_time = time.time()
    minute_requests = [t for t in key_data.get("minute_requests", []) if current_time - t < 60]
    
    if len(minute_requests) >= per_minute:
        return False, f"Rate limit exceeded ({per_minute} requests/minute)", None
    
    key_data["requests_today"] = key_data.get("requests_today", 0) + 1
    minute_requests.append(current_time)
    key_data["minute_requests"] = minute_requests
    
    keys[api_key] = key_data
    save_json("keys.json", keys)
    
    return True, "OK", key_data

# ==================== HTML TEMPLATES ====================
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Vehicle API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            width: 100%;
            max-width: 420px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        .logo { text-align: center; font-size: 60px; margin-bottom: 10px; }
        h1 { text-align: center; color: #fff; margin-bottom: 10px; font-size: 26px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 30px; font-size: 14px; }
        .input-group { margin-bottom: 20px; }
        label { color: #aaa; display: block; margin-bottom: 8px; font-size: 14px; }
        input {
            width: 100%; padding: 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px; color: #fff; font-size: 16px;
            transition: all 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 20px rgba(102,126,234,0.2); }
        button {
            width: 100%; padding: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border: none; border-radius: 10px;
            font-size: 18px; cursor: pointer; margin-top: 10px;
            transition: all 0.3s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102,126,234,0.3); }
        .error {
            color: #e74c3c; text-align: center; margin-top: 15px;
            padding: 12px; background: rgba(231,76,60,0.1);
            border-radius: 8px; border: 1px solid rgba(231,76,60,0.2);
        }
        .info { text-align: center; color: #666; margin-top: 20px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">🚗</div>
        <h1>Admin Panel</h1>
        <p class="subtitle">Vehicle API Management</p>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/admin/login">
            <div class="input-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit">🔐 Login</button>
        </form>
        <p class="info">Default: admin / admin123</p>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; }
        .header {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 20px 30px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            position: sticky; top: 0; z-index: 100;
        }
        .header h1 { font-size: 22px; }
        .header-right { display: flex; gap: 15px; align-items: center; }
        .user-badge { background: rgba(102,126,234,0.3); padding: 8px 15px; border-radius: 20px; font-size: 14px; }
        .logout-btn {
            background: #e74c3c; color: white; padding: 8px 20px;
            border-radius: 8px; text-decoration: none; font-size: 14px; transition: 0.3s;
        }
        .logout-btn:hover { background: #c0392b; }
        .container { max-width: 1400px; margin: 0 auto; padding: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);
        }
        .stat-card h3 { color: #888; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .stat-card .value { font-size: 36px; font-weight: bold; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .section {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 15px; padding: 25px; margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .section h2 { margin-bottom: 20px; font-size: 20px; display: flex; align-items: center; gap: 10px; }
        .btn {
            padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer;
            font-size: 14px; transition: all 0.3s; text-decoration: none; display: inline-block;
        }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.3); }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #f39c12; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        th { color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
        .badge {
            padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold;
            display: inline-block;
        }
        .badge-active { background: rgba(39,174,96,0.2); color: #27ae60; }
        .badge-inactive { background: rgba(231,76,60,0.2); color: #e74c3c; }
        .badge-free { background: rgba(52,152,219,0.2); color: #3498db; }
        .badge-admin { background: rgba(155,89,182,0.2); color: #9b59b6; }
        .badge-owner { background: rgba(241,196,15,0.2); color: #f1c40f; }
        .modal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: #1a1a2e; padding: 30px; border-radius: 15px;
            width: 90%; max-width: 500px; border: 1px solid rgba(255,255,255,0.1);
        }
        .modal-content h3 { margin-bottom: 20px; }
        .modal-content input, .modal-content select {
            width: 100%; padding: 12px; margin: 10px 0;
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; color: #fff; font-size: 14px;
        }
        .modal-content input:focus { outline: none; border-color: #667eea; }
        .modal-actions { display: flex; gap: 10px; margin-top: 20px; justify-content: flex-end; }
        .toast {
            position: fixed; top: 20px; right: 20px; padding: 15px 25px;
            border-radius: 10px; z-index: 9999; animation: slideIn 0.3s ease;
            font-weight: bold; display: none;
        }
        .toast-success { background: #27ae60; color: white; }
        .toast-error { background: #e74c3c; color: white; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .empty-state { text-align: center; padding: 40px; color: #666; }
        .action-btns { display: flex; gap: 8px; }
        .small-btn { padding: 5px 12px; font-size: 12px; border-radius: 5px; border: none; cursor: pointer; transition: 0.2s; }
        .small-btn:hover { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚗 Vehicle API Admin</h1>
        <div class="header-right">
            <span class="user-badge">👤 {{ session.get('user', 'admin') }}</span>
            <a href="/admin/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <h3>Total Keys</h3>
                <div class="value">{{ total_keys }}</div>
            </div>
            <div class="stat-card">
                <h3>Active Keys</h3>
                <div class="value">{{ active_keys }}</div>
            </div>
            <div class="stat-card">
                <h3>Total APIs</h3>
                <div class="value">{{ total_apis }}</div>
            </div>
            <div class="stat-card">
                <h3>Active APIs</h3>
                <div class="value">{{ active_apis }}</div>
            </div>
        </div>
        
        <!-- API Keys Section -->
        <div class="section">
            <h2>🔑 API Keys <button class="btn btn-primary" onclick="openModal('keyModal')" style="margin-left: auto;">+ Create Key</button></h2>
            <table>
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Expires</th>
                        <th>Daily Limit</th>
                        <th>Used Today</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for key_name, key_data in keys.items() %}
                    <tr>
                        <td><code>{{ key_name }}</code></td>
                        <td><span class="badge badge-{{ key_data.type.lower() }}">{{ key_data.type }}</span></td>
                        <td><span class="badge badge-{{ 'active' if key_data.status == 'active' else 'inactive' }}">{{ key_data.status }}</span></td>
                        <td>{{ 'Unlimited' if key_data.expires == 'unlimited' else key_data.expires[:10] }}</td>
                        <td>{{ 'Unlimited' if key_data.daily_limit == float('inf') or key_data.daily_limit == 'inf' else key_data.daily_limit }}</td>
                        <td>{{ key_data.get('requests_today', 0) }}</td>
                        <td class="action-btns">
                            <button class="small-btn btn-warning" onclick="toggleKey('{{ key_name }}')">{{ 'Deactivate' if key_data.status == 'active' else 'Activate' }}</button>
                            <button class="small-btn btn-danger" onclick="deleteKey('{{ key_name }}')">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- API Endpoints Section -->
        <div class="section">
            <h2>🔗 API Endpoints <button class="btn btn-primary" onclick="openModal('apiModal')" style="margin-left: auto;">+ Add API</button></h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>URL</th>
                        <th>Param</th>
                        <th>Status</th>
                        <th>Timeout</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for api_name, api_data in apis.items() %}
                    <tr>
                        <td><strong>{{ api_data.name }}</strong></td>
                        <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{{ api_data.url }}</td>
                        <td><code>{{ api_data.params.keys()|list|first }}</code></td>
                        <td><span class="badge badge-{{ 'active' if api_data.status == 'active' else 'inactive' }}">{{ api_data.status }}</span></td>
                        <td>{{ api_data.timeout }}s</td>
                        <td class="action-btns">
                            <button class="small-btn btn-warning" onclick="toggleApi('{{ api_name }}')">{{ 'Deactivate' if api_data.status == 'active' else 'Activate' }}</button>
                            <button class="small-btn btn-danger" onclick="deleteApi('{{ api_name }}')">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Usage Info -->
        <div class="section">
            <h2>📖 Usage Examples</h2>
            <pre style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; overflow-x: auto; font-size: 14px;">
# Basic Usage
GET /api?key=demo&api=rc&num=MH02FZ055

# Available Endpoints:
{% for api_name, api_data in apis.items() %}
/api?key=YOUR_KEY&api={{ api_name }}&{{ api_data.params.keys()|list|first }}=VEHICLE_NUMBER
{% endfor %}

# Response includes:
# - Real API data
# - _credits: { owner, brother, key_type, timestamp }</pre>
        </div>
    </div>
    
    <!-- Create Key Modal -->
    <div id="keyModal" class="modal">
        <div class="modal-content">
            <h3>🔑 Create New API Key</h3>
            <form id="createKeyForm">
                <input type="text" name="key_name" placeholder="Key Name (e.g., user123)" required>
                <select name="key_type" required>
                    <option value="FREE">FREE</option>
                    <option value="PREMIUM">PREMIUM</option>
                    <option value="ADMIN">ADMIN</option>
                    <option value="OWNER">OWNER</option>
                </select>
                <input type="number" name="expiry_days" placeholder="Expiry Days (0 = unlimited)" value="4" required>
                <input type="text" name="daily_limit" placeholder="Daily Limit (unlimited for no limit)" value="1000" required>
                <input type="text" name="per_minute_limit" placeholder="Per Minute Limit" value="80" required>
                <div class="modal-actions">
                    <button type="button" class="btn btn-danger" onclick="closeModal('keyModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Key</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Add API Modal -->
    <div id="apiModal" class="modal">
        <div class="modal-content">
            <h3>🔗 Add New API Endpoint</h3>
            <form id="createApiForm">
                <input type="text" name="api_name" placeholder="API Name (e.g., rc, vehicle)" required>
                <input type="text" name="api_url" placeholder="API URL (e.g., https://api.example.com/rc)" required>
                <input type="text" name="param_key" placeholder="Parameter Key (e.g., num, vehicle)" required>
                <input type="number" name="timeout" placeholder="Timeout in seconds" value="30" required>
                <div class="modal-actions">
                    <button type="button" class="btn btn-danger" onclick="closeModal('apiModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add API</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Toast -->
    <div id="toast" class="toast"></div>
    
    <script>
        function showToast(message, type) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = `toast toast-${type}`;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }
        
        function openModal(id) {
            document.getElementById(id).classList.add('active');
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        // Create Key
        document.getElementById('createKeyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const response = await fetch('/admin/keys/create', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                showToast(data.message, 'success');
                closeModal('keyModal');
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.error, 'error');
            }
        });
        
        // Add API
        document.getElementById('createApiForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const response = await fetch('/admin/apis/add', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                showToast(data.message, 'success');
                closeModal('apiModal');
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.error, 'error');
            }
        });
        
        // Toggle Key
        async function toggleKey(keyName) {
            const response = await fetch(`/admin/keys/toggle/${keyName}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                showToast(`Key ${data.status}`, 'success');
                setTimeout(() => location.reload(), 500);
            }
        }
        
        // Delete Key
        async function deleteKey(keyName) {
            if (confirm(`Delete key "${keyName}"?`)) {
                const response = await fetch(`/admin/keys/delete/${keyName}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => location.reload(), 500);
                }
            }
        }
        
        // Toggle API
        async function toggleApi(apiName) {
            const response = await fetch(`/admin/apis/toggle/${apiName}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                showToast(`API ${data.status}`, 'success');
                setTimeout(() => location.reload(), 500);
            }
        }
        
        // Delete API
        async function deleteApi(apiName) {
            if (confirm(`Delete API "${apiName}"?`)) {
                const response = await fetch(`/admin/apis/delete/${apiName}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => location.reload(), 500);
                }
            }
        }
    </script>
</body>
</html>
'''

# ==================== API ROUTES ====================
@app.route('/api')
def api_handler():
    """Main API endpoint - Masked"""
    valid, message, key_data = check_api_key()
    if not valid:
        return Response(json.dumps({"error": message}, indent=2), mimetype='application/json', status=401)
    
    api_name = request.args.get('api', 'rc')
    apis = load_json("apis.json")
    
    if api_name not in apis:
        return Response(json.dumps({"error": f"API '{api_name}' not found", "available": list(apis.keys())}, indent=2), mimetype='application/json', status=404)
    
    api_config = apis[api_name]
    
    if api_config.get("status") != "active":
        return Response(json.dumps({"error": "API currently inactive"}, indent=2), mimetype='application/json', status=403)
    
    # Get parameter value from configured param key
    param_value = None
    for param_key in api_config.get("params", {}).keys():
        param_value = request.args.get(param_key)
        break
    
    if not param_value:
        return Response(json.dumps({"error": f"Parameter '{param_key}' required"}, indent=2), mimetype='application/json', status=400)
    
    # Fetch from real API
    try:
        url = api_config["url"]
        params = {}
        for key, value in api_config.get("params", {}).items():
            params[key] = value.replace("{param}", param_value)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
        }
        
        timeout = api_config.get("timeout", 30)
        response = requests.get(url, params=params, headers=headers, timeout=timeout, verify=False)
        
        if response.status_code == 200:
            try:
                result = response.json()
            except:
                result = {"data": response.text}
        else:
            result = {"error": f"Upstream API returned status {response.status_code}"}
        
        # Add credits
        result["_credits"] = {
            "owner": "@ftgamer2",
            "brother": "@BRONX_ULTRA",
            "key_type": key_data.get("type", "UNKNOWN"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return Response(json.dumps(result, indent=2, ensure_ascii=False), mimetype='application/json; charset=utf-8')
        
    except requests.exceptions.Timeout:
        return Response(json.dumps({"error": "Upstream API timeout"}, indent=2), mimetype='application/json', status=504)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, indent=2), mimetype='application/json', status=500)

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
def login_page():
    """Login page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def login():
    """Handle login"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    users = load_json("users.json")
    
    if username in users:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password"] == hashed:
            session['user'] = username
            session['role'] = users[username].get("role", "admin")
            return redirect(url_for('dashboard'))
    
    return render_template_string(LOGIN_HTML, error="❌ Invalid credentials!")

@app.route('/admin/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    keys = load_json("keys.json")
    apis = load_json("apis.json")
    
    total_keys = len(keys)
    active_keys = sum(1 for k in keys.values() if k.get("status") == "active")
    total_apis = len(apis)
    active_apis = sum(1 for a in apis.values() if a.get("status") == "active")
    
    return render_template_string(DASHBOARD_HTML,
                                 keys=keys, apis=apis,
                                 total_keys=total_keys, active_keys=active_keys,
                                 total_apis=total_apis, active_apis=active_apis)

@app.route('/admin/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login_page'))

# ==================== KEY MANAGEMENT ====================
@app.route('/admin/keys/create', methods=['POST'])
@login_required
def create_key():
    """Create new API key"""
    key_name = request.form.get('key_name', '').strip()
    key_type = request.form.get('key_type', 'FREE')
    expiry_days = request.form.get('expiry_days', '4')
    daily_limit = request.form.get('daily_limit', '1000')
    per_minute_limit = request.form.get('per_minute_limit', '80')
    
    if not key_name:
        return jsonify({"error": "Key name required"}), 400
    
    keys = load_json("keys.json")
    
    if key_name in keys:
        return jsonify({"error": "Key already exists"}), 400
    
    try:
        expiry_days = int(expiry_days)
        daily_limit = float('inf') if daily_limit.lower() == 'unlimited' else int(daily_limit)
        per_minute_limit = float('inf') if per_minute_limit.lower() == 'unlimited' else int(per_minute_limit)
    except:
        return jsonify({"error": "Invalid limit values"}), 400
    
    keys[key_name] = {
        "key": key_name,
        "type": key_type,
        "expires": str(datetime.now() + timedelta(days=expiry_days)) if expiry_days > 0 else "unlimited",
        "daily_limit": daily_limit,
        "per_minute_limit": per_minute_limit,
        "requests_today": 0,
        "last_reset": datetime.now().strftime("%Y-%m-%d"),
        "minute_requests": [],
        "created": str(datetime.now()),
        "status": "active",
        "created_by": session.get('user', 'unknown')
    }
    
    save_json("keys.json", keys)
    return jsonify({"success": True, "message": f"✅ Key '{key_name}' created successfully!"})

@app.route('/admin/keys/delete/<key_name>', methods=['DELETE'])
@login_required
def delete_key(key_name):
    """Delete API key"""
    keys = load_json("keys.json")
    if key_name in keys:
        del keys[key_name]
        save_json("keys.json", keys)
        return jsonify({"success": True, "message": "Key deleted"})
    return jsonify({"error": "Key not found"}), 404

@app.route('/admin/keys/toggle/<key_name>', methods=['POST'])
@login_required
def toggle_key(key_name):
    """Toggle key status"""
    keys = load_json("keys.json")
    if key_name in keys:
        current = keys[key_name].get("status", "active")
        keys[key_name]["status"] = "inactive" if current == "active" else "active"
        save_json("keys.json", keys)
        return jsonify({"success": True, "status": keys[key_name]["status"]})
    return jsonify({"error": "Key not found"}), 404

# ==================== API MANAGEMENT ====================
@app.route('/admin/apis/add', methods=['POST'])
@login_required
def add_api():
    """Add new API endpoint"""
    api_name = request.form.get('api_name', '').strip()
    api_url = request.form.get('api_url', '').strip()
    param_key = request.form.get('param_key', '').strip()
    timeout = request.form.get('timeout', '30')
    
    if not all([api_name, api_url, param_key]):
        return jsonify({"error": "All fields required"}), 400
    
    apis = load_json("apis.json")
    
    if api_name in apis:
        return jsonify({"error": "API name already exists"}), 400
    
    try:
        timeout = int(timeout)
    except:
        timeout = 30
    
    apis[api_name] = {
        "name": api_name,
        "url": api_url,
        "params": {param_key: "{param}"},
        "method": "GET",
        "timeout": timeout,
        "status": "active",
        "added_by": session.get('user', 'unknown'),
        "created": str(datetime.now())
    }
    
    save_json("apis.json", apis)
    return jsonify({"success": True, "message": f"✅ API '{api_name}' added successfully!"})

@app.route('/admin/apis/delete/<api_name>', methods=['DELETE'])
@login_required
def delete_api(api_name):
    """Delete API endpoint"""
    apis = load_json("apis.json")
    if api_name in apis:
        del apis[api_name]
        save_json("apis.json", apis)
        return jsonify({"success": True, "message": "API deleted"})
    return jsonify({"error": "API not found"}), 404

@app.route('/admin/apis/toggle/<api_name>', methods=['POST'])
@login_required
def toggle_api(api_name):
    """Toggle API status"""
    apis = load_json("apis.json")
    if api_name in apis:
        current = apis[api_name].get("status", "active")
        apis[api_name]["status"] = "inactive" if current == "active" else "active"
        save_json("apis.json", apis)
        return jsonify({"success": True, "status": apis[api_name]["status"]})
    return jsonify({"error": "API not found"}), 404

# ==================== HOME ====================
@app.route('/')
def home():
    """Home page"""
    apis = load_json("apis.json")
    return jsonify({
        "status": "🚗 Vehicle API Running ✅",
        "version": "3.0 - All in One",
        "admin_panel": "/admin",
        "usage": "/api?key=YOUR_KEY&api=API_NAME&PARAM=VALUE",
        "example": "/api?key=demo&api=rc&num=MH02FZ055",
        "available_apis": list(apis.keys()),
        "available_keys": ["demo", "admin-op", "ft-op"],
        "features": [
            "API Key System with Rate Limiting",
            "Dynamic API Endpoint Management",
            "Admin Dashboard with UI",
            "Custom Expiry Dates for Keys",
            "Add/Remove APIs on the fly",
            "Credits: @ftgamer2 & @BRONX_ULTRA"
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
