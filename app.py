from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, Response
import requests
import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_json(filename, default=None):
    if default is None: default = {}
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return default

def save_json(filename, data):
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# Initialize
if not (DATA_DIR / "users.json").exists():
    save_json("users.json", {
        "BRONX": {
            "password": hashlib.sha256("BRONX@2024".encode()).hexdigest(),
            "role": "owner"
        }
    })

if not (DATA_DIR / "keys.json").exists():
    save_json("keys.json", {})

if not (DATA_DIR / "apis.json").exists():
    save_json("apis.json", {})

if not (DATA_DIR / "settings.json").exists():
    save_json("settings.json", {
        "site_name": "BRONX Ultra OSINT",
        "owner": "@BRONX_ULTRA",
        "public_access": False,
        "show_keys": False
    })

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'owner':
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function

def check_api_key():
    settings = load_json("settings.json")
    
    # If public access is off, require key
    api_key = request.args.get('key', '') or request.headers.get('X-API-Key', '')
    
    if not api_key:
        return False, "API Key Required - Contact @BRONX_ULTRA", None
    
    keys = load_json("keys.json")
    
    if api_key not in keys:
        return False, "Invalid API Key", None
    
    key_data = keys[api_key]
    
    if key_data.get("status") != "active":
        return False, "Key Inactive", None
    
    if key_data.get("expires") != "unlimited":
        try:
            expiry = datetime.fromisoformat(key_data["expires"])
            if datetime.now() > expiry:
                return False, "Key Expired", None
        except: pass
    
    today = datetime.now().strftime("%Y-%m-%d")
    if key_data.get("last_reset") != today:
        key_data["requests_today"] = 0
        key_data["last_reset"] = today
        key_data["minute_requests"] = []
    
    daily_limit = key_data.get("daily_limit", float('inf'))
    if isinstance(daily_limit, str):
        daily_limit = float('inf') if daily_limit == 'inf' else int(daily_limit)
    
    if key_data.get("requests_today", 0) >= daily_limit:
        return False, "Daily Limit Reached", None
    
    per_minute = key_data.get("per_minute_limit", float('inf'))
    if isinstance(per_minute, str):
        per_minute = float('inf') if per_minute == 'inf' else int(per_minute)
    
    current_time = time.time()
    minute_requests = [t for t in key_data.get("minute_requests", []) if current_time - t < 60]
    
    if len(minute_requests) >= per_minute:
        return False, "Rate Limit Exceeded", None
    
    key_data["requests_today"] = key_data.get("requests_today", 0) + 1
    key_data["total_requests"] = key_data.get("total_requests", 0) + 1
    minute_requests.append(current_time)
    key_data["minute_requests"] = minute_requests
    
    keys[api_key] = key_data
    save_json("keys.json", keys)
    
    return True, "OK", key_data

# ==================== TEMPLATES ====================
LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRONX Ultra OSINT - Login</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            background:linear-gradient(135deg,#000000,#1a0000,#000000);
            min-height:100vh;display:flex;justify-content:center;align-items:center;
            font-family:'Courier New',monospace;
        }
        .matrix-bg{position:fixed;top:0;left:0;width:100%;height:100%;opacity:0.03;z-index:0}
        .login-box{
            background:rgba(0,0,0,0.8);backdrop-filter:blur(20px);
            border:1px solid rgba(255,0,0,0.2);border-radius:5px;
            padding:50px 40px;width:100%;max-width:420px;
            position:relative;z-index:1;
            box-shadow:0 0 50px rgba(255,0,0,0.1);
        }
        .logo-text{
            text-align:center;font-size:14px;color:#ff0000;
            letter-spacing:3px;margin-bottom:5px;
        }
        h1{
            text-align:center;color:#fff;font-size:24px;
            margin-bottom:5px;letter-spacing:2px;
        }
        .subtitle{text-align:center;color:#666;font-size:11px;margin-bottom:30px;letter-spacing:2px}
        .input-group{margin-bottom:20px}
        label{color:#888;display:block;margin-bottom:8px;font-size:12px;letter-spacing:1px}
        input{
            width:100%;padding:14px;background:rgba(255,0,0,0.05);
            border:1px solid rgba(255,0,0,0.2);color:#fff;font-size:14px;
            font-family:'Courier New',monospace;transition:all 0.3s;
        }
        input:focus{outline:none;border-color:#ff0000;box-shadow:0 0 20px rgba(255,0,0,0.2)}
        button{
            width:100%;padding:15px;background:linear-gradient(135deg,#8b0000,#ff0000);
            color:#fff;border:none;font-size:16px;cursor:pointer;
            font-family:'Courier New',monospace;letter-spacing:2px;
            transition:all 0.3s;margin-top:10px;
        }
        button:hover{box-shadow:0 0 30px rgba(255,0,0,0.5)}
        .error{
            color:#ff0000;text-align:center;padding:12px;
            background:rgba(255,0,0,0.1);border:1px solid rgba(255,0,0,0.2);
            margin-top:15px;font-size:12px;
        }
        .footer{text-align:center;color:#333;margin-top:20px;font-size:10px;letter-spacing:1px}
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo-text">■ BRONX ULTRA ■</div>
        <h1>OSINT SERVER</h1>
        <p class="subtitle">RESTRICTED ACCESS</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" action="/admin/login">
            <div class="input-group">
                <label>USERNAME</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="input-group">
                <label>PASSWORD</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit">ACCESS PANEL</button>
        </form>
        <div class="footer">© @BRONX_ULTRA</div>
    </div>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRONX Ultra OSINT - Dashboard</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        ::-webkit-scrollbar{width:5px}
        ::-webkit-scrollbar-track{background:#000}
        ::-webkit-scrollbar-thumb{background:#ff0000}
        body{
            background:#000;color:#fff;font-family:'Courier New',monospace;
            min-height:100vh;
        }
        .header{
            background:linear-gradient(135deg,#0a0000,#1a0000);
            border-bottom:1px solid rgba(255,0,0,0.2);
            padding:15px 30px;display:flex;justify-content:space-between;
            align-items:center;position:sticky;top:0;z-index:100;
        }
        .header h1{font-size:16px;letter-spacing:2px;color:#ff0000}
        .header-right{display:flex;gap:15px;align-items:center}
        .user-tag{
            background:rgba(255,0,0,0.1);border:1px solid rgba(255,0,0,0.2);
            padding:6px 15px;font-size:11px;letter-spacing:1px;
        }
        .logout-btn{
            background:rgba(255,0,0,0.2);color:#ff0000;padding:6px 15px;
            text-decoration:none;font-size:11px;letter-spacing:1px;
            border:1px solid rgba(255,0,0,0.3);transition:0.3s;
        }
        .logout-btn:hover{background:rgba(255,0,0,0.4)}
        .container{max-width:1500px;margin:0 auto;padding:20px}
        .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px;margin-bottom:25px}
        .stat-card{
            background:linear-gradient(135deg,#0a0a0a,#111);
            border:1px solid rgba(255,0,0,0.1);padding:20px;
        }
        .stat-card .label{color:#666;font-size:10px;letter-spacing:2px;margin-bottom:8px}
        .stat-card .value{font-size:28px;color:#ff0000;font-weight:bold}
        .section{
            background:linear-gradient(135deg,#0a0a0a,#111);
            border:1px solid rgba(255,0,0,0.1);padding:25px;margin-bottom:20px;
        }
        .section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
        .section-header h2{font-size:14px;letter-spacing:2px;color:#ff0000}
        .btn{
            padding:8px 18px;border:1px solid rgba(255,0,0,0.3);cursor:pointer;
            font-family:'Courier New',monospace;font-size:11px;letter-spacing:1px;
            transition:0.3s;background:rgba(255,0,0,0.1);color:#ff0000;
        }
        .btn:hover{background:rgba(255,0,0,0.3);box-shadow:0 0 15px rgba(255,0,0,0.2)}
        .btn-green{background:rgba(0,255,0,0.1);border-color:rgba(0,255,0,0.3);color:#0f0}
        .btn-green:hover{background:rgba(0,255,0,0.3)}
        .btn-yellow{background:rgba(255,255,0,0.1);border-color:rgba(255,255,0,0.3);color:#ff0}
        .btn-yellow:hover{background:rgba(255,255,0,0.3)}
        table{width:100%;border-collapse:collapse;font-size:11px}
        th{
            text-align:left;padding:12px 10px;border-bottom:1px solid rgba(255,0,0,0.1);
            color:#666;font-size:10px;letter-spacing:1px;
        }
        td{padding:12px 10px;border-bottom:1px solid rgba(255,0,0,0.05)}
        .badge{
            padding:3px 10px;border:1px solid;font-size:9px;letter-spacing:1px;
            display:inline-block;
        }
        .badge-active{color:#0f0;border-color:rgba(0,255,0,0.3)}
        .badge-inactive{color:#f00;border-color:rgba(255,0,0,0.3)}
        .badge-owner{color:#ff0;border-color:rgba(255,255,0,0.3)}
        .badge-vip{color:#f0f;border-color:rgba(255,0,255,0.3)}
        code{
            background:rgba(255,0,0,0.1);padding:2px 8px;color:#ff0000;
            font-size:10px;letter-spacing:1px;
        }
        .modal{
            display:none;position:fixed;top:0;left:0;width:100%;height:100%;
            background:rgba(0,0,0,0.9);z-index:1000;
            justify-content:center;align-items:center;
        }
        .modal.active{display:flex}
        .modal-content{
            background:#0a0a0a;border:1px solid rgba(255,0,0,0.2);
            padding:30px;width:90%;max-width:500px;
        }
        .modal-content h3{color:#ff0000;letter-spacing:2px;margin-bottom:20px;font-size:14px}
        input,select{
            width:100%;padding:12px;margin:10px 0;
            background:#000;border:1px solid rgba(255,0,0,0.2);
            color:#fff;font-family:'Courier New',monospace;font-size:12px;
        }
        input:focus,select:focus{outline:none;border-color:#ff0000}
        .modal-actions{display:flex;gap:10px;margin-top:20px;justify-content:flex-end}
        .toast{
            position:fixed;top:20px;right:20px;padding:15px 25px;
            border:1px solid;z-index:9999;font-size:11px;letter-spacing:1px;
            display:none;animation:slideIn 0.3s ease;
        }
        .toast-success{border-color:#0f0;color:#0f0;background:rgba(0,255,0,0.1)}
        .toast-error{border-color:#f00;color:#f00;background:rgba(255,0,0,0.1)}
        @keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
        .empty{text-align:center;color:#333;padding:30px;font-size:11px;letter-spacing:2px}
        .api-url{
            background:#000;padding:15px;border:1px solid rgba(255,0,0,0.1);
            font-size:11px;letter-spacing:1px;color:#0f0;overflow-x:auto;
            margin-top:10px;
        }
        .toggle-switch{
            position:relative;display:inline-block;width:50px;height:24px;
        }
        .toggle-switch input{opacity:0;width:0;height:0}
        .slider{
            position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;
            background:#1a0000;border:1px solid rgba(255,0,0,0.3);transition:0.3s;
        }
        .slider:before{
            position:absolute;content:"";height:16px;width:16px;
            left:3px;bottom:3px;background:#ff0000;transition:0.3s;
        }
        input:checked+.slider{background:#001a00;border-color:#0f0}
        input:checked+.slider:before{transform:translateX(26px);background:#0f0}
        .action-btns{display:flex;gap:5px}
    </style>
</head>
<body>
    <div class="header">
        <h1>■ BRONX ULTRA OSINT</h1>
        <div class="header-right">
            <span class="user-tag">{{ session.get('user','OWNER') }}</span>
            <a href="/admin/logout" class="logout-btn">EXIT</a>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">ACTIVE KEYS</div>
                <div class="value">{{ active_keys }}</div>
            </div>
            <div class="stat-card">
                <div class="label">TOTAL APIs</div>
                <div class="value">{{ total_apis }}</div>
            </div>
            <div class="stat-card">
                <div class="label">TOTAL REQUESTS</div>
                <div class="value">{{ total_requests }}</div>
            </div>
            <div class="stat-card">
                <div class="label">SERVER STATUS</div>
                <div class="value" style="color:#0f0">ONLINE</div>
            </div>
        </div>
        
        <!-- Settings -->
        <div class="section">
            <div class="section-header">
                <h2>⚙ SERVER SETTINGS</h2>
            </div>
            <table>
                <tr>
                    <td>Public Access (No Key Required)</td>
                    <td>
                        <label class="toggle-switch">
                            <input type="checkbox" {{ 'checked' if settings.public_access else '' }} onchange="toggleSetting('public_access')">
                            <span class="slider"></span>
                        </label>
                    </td>
                </tr>
                <tr>
                    <td>Show Keys in Dashboard</td>
                    <td>
                        <label class="toggle-switch">
                            <input type="checkbox" {{ 'checked' if settings.show_keys else '' }} onchange="toggleSetting('show_keys')">
                            <span class="slider"></span>
                        </label>
                    </td>
                </tr>
            </table>
        </div>
        
        <!-- API Keys -->
        <div class="section">
            <div class="section-header">
                <h2>🔑 API KEYS</h2>
                <button class="btn" onclick="openModal('keyModal')">+ CREATE KEY</button>
            </div>
            {% if keys %}
            <table>
                <thead>
                    <tr>
                        <th>KEY</th>
                        <th>TYPE</th>
                        <th>STATUS</th>
                        <th>EXPIRES</th>
                        <th>TODAY</th>
                        <th>TOTAL</th>
                        <th>ACTIONS</th>
                    </tr>
                </thead>
                <tbody>
                    {% for key_name, key_data in keys.items() %}
                    <tr>
                        <td>
                            {% if settings.show_keys %}
                            <code>{{ key_name }}</code>
                            {% else %}
                            <code>••••••••</code>
                            {% endif %}
                        </td>
                        <td><span class="badge badge-{{ key_data.type.lower() }}">{{ key_data.type }}</span></td>
                        <td><span class="badge badge-{{ 'active' if key_data.status=='active' else 'inactive' }}">{{ key_data.status.upper() }}</span></td>
                        <td>{{ '∞' if key_data.expires=='unlimited' else key_data.expires[:10] }}</td>
                        <td>{{ key_data.get('requests_today',0) }}</td>
                        <td>{{ key_data.get('total_requests',0) }}</td>
                        <td class="action-btns">
                            <button class="btn btn-yellow" onclick="toggleKey('{{ key_name }}')">{{ 'OFF' if key_data.status=='active' else 'ON' }}</button>
                            <button class="btn" onclick="deleteKey('{{ key_name }}')">DEL</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">NO KEYS CREATED</div>
            {% endif %}
        </div>
        
        <!-- APIs -->
        <div class="section">
            <div class="section-header">
                <h2>🔗 OSINT APIs</h2>
                <button class="btn btn-green" onclick="openModal('apiModal')">+ ADD API</button>
            </div>
            {% if apis %}
            <table>
                <thead>
                    <tr>
                        <th>NAME</th>
                        <th>URL</th>
                        <th>STATUS</th>
                        <th>ACTIONS</th>
                    </tr>
                </thead>
                <tbody>
                    {% for api_name, api_data in apis.items() %}
                    <tr>
                        <td style="color:#ff0000">{{ api_data.name.upper() }}</td>
                        <td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;font-size:10px;color:#666">{{ api_data.url }}</td>
                        <td><span class="badge badge-{{ 'active' if api_data.status=='active' else 'inactive' }}">{{ api_data.status.upper() }}</span></td>
                        <td class="action-btns">
                            <button class="btn btn-yellow" onclick="toggleApi('{{ api_name }}')">{{ 'OFF' if api_data.status=='active' else 'ON' }}</button>
                            <button class="btn" onclick="deleteApi('{{ api_name }}')">DEL</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">NO APIs ADDED - ADD YOUR FIRST OSINT API</div>
            {% endif %}
        </div>
        
        <!-- API Usage -->
        <div class="section">
            <div class="section-header">
                <h2>📡 API USAGE FORMAT</h2>
            </div>
            <div class="api-url">
                {{ request.host_url }}api?key=YOUR_KEY&api=API_NAME&PARAM=VALUE
            </div>
            {% if apis %}
            <div style="margin-top:15px">
                {% for api_name, api_data in apis.items() %}
                <div class="api-url" style="margin-top:5px">
                    {{ request.host_url }}api?key=KEY&api={{ api_name }}&{{ api_data.params.keys()|list|first }}=VALUE
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <!-- Create Key Modal -->
    <div id="keyModal" class="modal">
        <div class="modal-content">
            <h3>■ CREATE NEW API KEY</h3>
            <form id="createKeyForm">
                <input type="text" name="key_name" placeholder="KEY NAME" required>
                <select name="key_type" required>
                    <option value="VIP">VIP</option>
                    <option value="PREMIUM">PREMIUM</option>
                    <option value="OWNER">OWNER</option>
                </select>
                <input type="number" name="expiry_days" placeholder="EXPIRY DAYS (0=UNLIMITED)" value="30" required>
                <input type="text" name="daily_limit" placeholder="DAILY LIMIT" value="1000" required>
                <input type="text" name="per_minute_limit" placeholder="PER MINUTE LIMIT" value="60" required>
                <div class="modal-actions">
                    <button type="button" class="btn" onclick="closeModal('keyModal')">CANCEL</button>
                    <button type="submit" class="btn btn-green">CREATE</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Add API Modal -->
    <div id="apiModal" class="modal">
        <div class="modal-content">
            <h3>■ ADD OSINT API</h3>
            <form id="createApiForm">
                <input type="text" name="api_name" placeholder="API NAME (e.g., vehicle)" required>
                <input type="text" name="api_url" placeholder="API URL (e.g., https://api.com/rc)" required>
                <input type="text" name="param_key" placeholder="PARAMETER KEY (e.g., num)" required>
                <input type="number" name="timeout" placeholder="TIMEOUT SECONDS" value="30" required>
                <div class="modal-actions">
                    <button type="button" class="btn" onclick="closeModal('apiModal')">CANCEL</button>
                    <button type="submit" class="btn btn-green">ADD API</button>
                </div>
            </form>
        </div>
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        function showToast(msg,type){
            const t=document.getElementById('toast');
            t.textContent=msg;t.className='toast toast-'+type;t.style.display='block';
            setTimeout(()=>t.style.display='none',3000);
        }
        function openModal(id){document.getElementById(id).classList.add('active')}
        function closeModal(id){document.getElementById(id).classList.remove('active')}
        
        document.getElementById('createKeyForm').addEventListener('submit',async(e)=>{
            e.preventDefault();
            const fd=new FormData(e.target);
            const r=await fetch('/admin/keys/create',{method:'POST',body:fd});
            const d=await r.json();
            showToast(d.success?d.message:d.error,d.success?'success':'error');
            if(d.success){closeModal('keyModal');setTimeout(()=>location.reload(),1000)}
        });
        
        document.getElementById('createApiForm').addEventListener('submit',async(e)=>{
            e.preventDefault();
            const fd=new FormData(e.target);
            const r=await fetch('/admin/apis/add',{method:'POST',body:fd});
            const d=await r.json();
            showToast(d.success?d.message:d.error,d.success?'success':'error');
            if(d.success){closeModal('apiModal');setTimeout(()=>location.reload(),1000)}
        });
        
        async function toggleKey(name){
            const r=await fetch('/admin/keys/toggle/'+name,{method:'POST'});
            const d=await r.json();
            showToast('Key '+d.status,d.success?'success':'error');
            setTimeout(()=>location.reload(),500);
        }
        
        async function deleteKey(name){
            if(confirm('DELETE KEY: '+name+'?')){
                const r=await fetch('/admin/keys/delete/'+name,{method:'DELETE'});
                const d=await r.json();
                showToast(d.message,'success');
                setTimeout(()=>location.reload(),500);
            }
        }
        
        async function toggleApi(name){
            const r=await fetch('/admin/apis/toggle/'+name,{method:'POST'});
            const d=await r.json();
            showToast('API '+d.status,d.success?'success':'error');
            setTimeout(()=>location.reload(),500);
        }
        
        async function deleteApi(name){
            if(confirm('DELETE API: '+name+'?')){
                const r=await fetch('/admin/apis/delete/'+name,{method:'DELETE'});
                const d=await r.json();
                showToast(d.message,'success');
                setTimeout(()=>location.reload(),500);
            }
        }
        
        async function toggleSetting(setting){
            const r=await fetch('/admin/settings/toggle/'+setting,{method:'POST'});
            const d=await r.json();
            showToast('Setting Updated','success');
            setTimeout(()=>location.reload(),500);
        }
    </script>
</body>
</html>
'''

# ==================== PUBLIC ROUTES ====================
@app.route('/')
def home():
    """Public home - Only shows BRONX Server Status"""
    settings = load_json("settings.json")
    return jsonify({
        "server": "BRONX Ultra OSINT",
        "status": "ONLINE",
        "owner": "@BRONX_ULTRA",
        "access": "RESTRICTED - API Key Required",
        "contact": "Contact @BRONX_ULTRA for access"
    })

@app.route('/api')
def api_handler():
    """Main API endpoint"""
    valid, message, key_data = check_api_key()
    if not valid:
        return Response(json.dumps({"error": message}, indent=2), mimetype='application/json', status=401)
    
    api_name = request.args.get('api', '')
    apis = load_json("apis.json")
    
    if not api_name or api_name not in apis:
        return Response(json.dumps({"error": "API not found"}, indent=2), mimetype='application/json', status=404)
    
    api_config = apis[api_name]
    
    if api_config.get("status") != "active":
        return Response(json.dumps({"error": "API inactive"}, indent=2), mimetype='application/json', status=403)
    
    param_value = None
    for param_key in api_config.get("params", {}).keys():
        param_value = request.args.get(param_key)
        break
    
    if not param_value:
        return Response(json.dumps({"error": "Parameter required"}, indent=2), mimetype='application/json', status=400)
    
    try:
        url = api_config["url"]
        params = {}
        for key, value in api_config.get("params", {}).items():
            params[key] = value.replace("{param}", param_value)
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=api_config.get("timeout", 30), verify=False)
        
        if response.status_code == 200:
            try:
                result = response.json()
            except:
                result = {"data": response.text}
        else:
            result = {"error": f"Status: {response.status_code}"}
        
        result["_credit"] = "@BRONX_ULTRA"
        
        return Response(json.dumps(result, indent=2, ensure_ascii=False), mimetype='application/json; charset=utf-8')
        
    except Exception as e:
        return Response(json.dumps({"error": str(e)}, indent=2), mimetype='application/json', status=500)

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_PAGE)

@app.route('/admin/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    users = load_json("users.json")
    
    if username in users:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password"] == hashed:
            session['user'] = username
            session['role'] = users[username].get("role", "owner")
            return redirect(url_for('dashboard'))
    
    return render_template_string(LOGIN_PAGE, error="ACCESS DENIED")

@app.route('/admin/dashboard')
@login_required
def dashboard():
    keys = load_json("keys.json")
    apis = load_json("apis.json")
    settings = load_json("settings.json")
    
    active_keys = sum(1 for k in keys.values() if k.get("status") == "active")
    total_apis = len(apis)
    total_requests = sum(k.get("total_requests", 0) for k in keys.values())
    
    return render_template_string(DASHBOARD_PAGE,
        keys=keys, apis=apis, settings=settings,
        active_keys=active_keys, total_apis=total_apis,
        total_requests=total_requests)

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ==================== SETTINGS ====================
@app.route('/admin/settings/toggle/<setting>', methods=['POST'])
@login_required
def toggle_setting(setting):
    settings = load_json("settings.json")
    if setting in settings:
        settings[setting] = not settings[setting]
        save_json("settings.json", settings)
        return jsonify({"success": True})
    return jsonify({"error": "Invalid setting"}), 400

# ==================== KEY MANAGEMENT ====================
@app.route('/admin/keys/create', methods=['POST'])
@login_required
def create_key():
    key_name = request.form.get('key_name', '').strip()
    key_type = request.form.get('key_type', 'VIP')
    expiry_days = request.form.get('expiry_days', '30')
    daily_limit = request.form.get('daily_limit', '1000')
    per_minute_limit = request.form.get('per_minute_limit', '60')
    
    if not key_name:
        return jsonify({"error": "Key name required"}), 400
    
    keys = load_json("keys.json")
    if key_name in keys:
        return jsonify({"error": "Key exists"}), 400
    
    try:
        expiry_days = int(expiry_days)
        daily_limit = float('inf') if daily_limit.lower() == 'unlimited' else int(daily_limit)
        per_minute_limit = float('inf') if per_minute_limit.lower() == 'unlimited' else int(per_minute_limit)
    except:
        return jsonify({"error": "Invalid values"}), 400
    
    keys[key_name] = {
        "key": key_name,
        "type": key_type,
        "expires": str(datetime.now() + timedelta(days=expiry_days)) if expiry_days > 0 else "unlimited",
        "daily_limit": daily_limit,
        "per_minute_limit": per_minute_limit,
        "requests_today": 0,
        "total_requests": 0,
        "last_reset": datetime.now().strftime("%Y-%m-%d"),
        "minute_requests": [],
        "status": "active",
        "created": str(datetime.now()),
        "created_by": session.get('user')
    }
    
    save_json("keys.json", keys)
    return jsonify({"success": True, "message": f"Key {key_name} Created"})

@app.route('/admin/keys/delete/<key_name>', methods=['DELETE'])
@login_required
def delete_key(key_name):
    keys = load_json("keys.json")
    if key_name in keys:
        del keys[key_name]
        save_json("keys.json", keys)
        return jsonify({"success": True, "message": "Deleted"})
    return jsonify({"error": "Not found"}), 404

@app.route('/admin/keys/toggle/<key_name>', methods=['POST'])
@login_required
def toggle_key(key_name):
    keys = load_json("keys.json")
    if key_name in keys:
        keys[key_name]["status"] = "inactive" if keys[key_name].get("status") == "active" else "active"
        save_json("keys.json", keys)
        return jsonify({"success": True, "status": keys[key_name]["status"]})
    return jsonify({"error": "Not found"}), 404

# ==================== API MANAGEMENT ====================
@app.route('/admin/apis/add', methods=['POST'])
@login_required
def add_api():
    api_name = request.form.get('api_name', '').strip()
    api_url = request.form.get('api_url', '').strip()
    param_key = request.form.get('param_key', '').strip()
    timeout = request.form.get('timeout', '30')
    
    if not all([api_name, api_url, param_key]):
        return jsonify({"error": "All fields required"}), 400
    
    apis = load_json("apis.json")
    if api_name in apis:
        return jsonify({"error": "API exists"}), 400
    
    apis[api_name] = {
        "name": api_name,
        "url": api_url,
        "params": {param_key: "{param}"},
        "method": "GET",
        "timeout": int(timeout) if timeout.isdigit() else 30,
        "status": "active",
        "added_by": session.get('user'),
        "created": str(datetime.now())
    }
    
    save_json("apis.json", apis)
    return jsonify({"success": True, "message": f"API {api_name} Added"})

@app.route('/admin/apis/delete/<api_name>', methods=['DELETE'])
@login_required
def delete_api(api_name):
    apis = load_json("apis.json")
    if api_name in apis:
        del apis[api_name]
        save_json("apis.json", apis)
        return jsonify({"success": True, "message": "Deleted"})
    return jsonify({"error": "Not found"}), 404

@app.route('/admin/apis/toggle/<api_name>', methods=['POST'])
@login_required
def toggle_api(api_name):
    apis = load_json("apis.json")
    if api_name in apis:
        apis[api_name]["status"] = "inactive" if apis[api_name].get("status") == "active" else "active"
        save_json("apis.json", apis)
        return jsonify({"success": True, "status": apis[api_name]["status"]})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
