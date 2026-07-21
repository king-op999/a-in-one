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
    save_json("keys.json", {
        "demo": {
            "key": "demo",
            "type": "VIP",
            "expires": str(datetime.now() + timedelta(days=30)),
            "daily_limit": 1000,
            "per_minute_limit": 60,
            "requests_today": 0,
            "total_requests": 0,
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
            "minute_requests": [],
            "status": "active",
            "created": str(datetime.now()),
            "created_by": "system"
        }
    })

if not (DATA_DIR / "apis.json").exists():
    save_json("apis.json", {
        "rc": {
            "name": "rc",
            "url": "https://simple-rc-info.vercel.app/rc",
            "params": {"num": "{param}"},
            "method": "GET",
            "timeout": 30,
            "status": "active",
            "added_by": "system",
            "created": str(datetime.now())
        }
    })

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

def check_api_key():
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
        body{background:#000;min-height:100vh;display:flex;justify-content:center;align-items:center;font-family:'Courier New',monospace}
        .login-box{background:rgba(0,0,0,0.9);border:1px solid rgba(255,0,0,0.3);padding:50px 40px;width:100%;max-width:420px;box-shadow:0 0 50px rgba(255,0,0,0.1)}
        h1{text-align:center;color:#ff0000;font-size:20px;letter-spacing:3px;margin-bottom:5px}
        .sub{text-align:center;color:#666;font-size:10px;letter-spacing:2px;margin-bottom:30px}
        label{color:#888;display:block;margin-bottom:8px;font-size:11px;letter-spacing:1px}
        input{width:100%;padding:14px;background:rgba(255,0,0,0.05);border:1px solid rgba(255,0,0,0.2);color:#fff;font-size:13px;font-family:'Courier New',monospace;margin-bottom:15px}
        input:focus{outline:none;border-color:#ff0000}
        button{width:100%;padding:15px;background:#8b0000;color:#fff;border:none;font-size:14px;cursor:pointer;font-family:'Courier New',monospace;letter-spacing:2px;transition:0.3s}
        button:hover{background:#ff0000;box-shadow:0 0 30px rgba(255,0,0,0.3)}
        .error{color:#ff0000;text-align:center;padding:10px;background:rgba(255,0,0,0.1);border:1px solid rgba(255,0,0,0.2);margin-top:15px;font-size:11px}
        .footer{text-align:center;color:#333;margin-top:20px;font-size:9px;letter-spacing:1px}
    </style>
</head>
<body>
    <div class="login-box">
        <h1>■ BRONX ULTRA OSINT</h1>
        <p class="sub">RESTRICTED ACCESS</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" action="/admin/login">
            <label>USERNAME</label>
            <input type="text" name="username" placeholder="Enter username" required>
            <label>PASSWORD</label>
            <input type="password" name="password" placeholder="Enter password" required>
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
        body{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh}
        .header{background:#0a0000;border-bottom:1px solid rgba(255,0,0,0.2);padding:15px 30px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}
        .header h1{font-size:14px;letter-spacing:2px;color:#ff0000}
        .header-right{display:flex;gap:15px;align-items:center}
        .user-tag{background:rgba(255,0,0,0.1);border:1px solid rgba(255,0,0,0.2);padding:6px 15px;font-size:10px}
        .logout-btn{background:rgba(255,0,0,0.2);color:#ff0000;padding:6px 15px;text-decoration:none;font-size:10px;border:1px solid rgba(255,0,0,0.3);transition:0.3s}
        .logout-btn:hover{background:rgba(255,0,0,0.4)}
        .container{max-width:1500px;margin:0 auto;padding:20px}
        .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:25px}
        .stat-card{background:#0a0a0a;border:1px solid rgba(255,0,0,0.1);padding:20px}
        .stat-card .label{color:#666;font-size:9px;letter-spacing:2px;margin-bottom:8px}
        .stat-card .value{font-size:28px;color:#ff0000;font-weight:bold}
        .section{background:#0a0a0a;border:1px solid rgba(255,0,0,0.1);padding:25px;margin-bottom:20px}
        .section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
        .section-header h2{font-size:13px;letter-spacing:2px;color:#ff0000}
        .btn{padding:8px 18px;border:1px solid rgba(255,0,0,0.3);cursor:pointer;font-family:'Courier New',monospace;font-size:10px;letter-spacing:1px;transition:0.3s;background:rgba(255,0,0,0.1);color:#ff0000}
        .btn:hover{background:rgba(255,0,0,0.3);box-shadow:0 0 15px rgba(255,0,0,0.2)}
        .btn-green{background:rgba(0,255,0,0.1);border-color:rgba(0,255,0,0.3);color:#0f0}
        .btn-green:hover{background:rgba(0,255,0,0.3)}
        .btn-yellow{background:rgba(255,255,0,0.1);border-color:rgba(255,255,0,0.3);color:#ff0}
        .btn-yellow:hover{background:rgba(255,255,0,0.3)}
        table{width:100%;border-collapse:collapse;font-size:10px}
        th{text-align:left;padding:12px 10px;border-bottom:1px solid rgba(255,0,0,0.1);color:#666;font-size:9px;letter-spacing:1px}
        td{padding:12px 10px;border-bottom:1px solid rgba(255,0,0,0.05)}
        .badge{padding:3px 10px;border:1px solid;font-size:8px;letter-spacing:1px;display:inline-block}
        .badge-active{color:#0f0;border-color:rgba(0,255,0,0.3)}
        .badge-inactive{color:#f00;border-color:rgba(255,0,0,0.3)}
        .badge-vip{color:#f0f;border-color:rgba(255,0,255,0.3)}
        code{background:rgba(255,0,0,0.1);padding:2px 8px;color:#ff0000;font-size:9px}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:1000;justify-content:center;align-items:center}
        .modal.active{display:flex}
        .modal-content{background:#0a0a0a;border:1px solid rgba(255,0,0,0.2);padding:30px;width:90%;max-width:500px}
        .modal-content h3{color:#ff0000;letter-spacing:2px;margin-bottom:20px;font-size:13px}
        input,select{width:100%;padding:12px;margin:10px 0;background:#000;border:1px solid rgba(255,0,0,0.2);color:#fff;font-family:'Courier New',monospace;font-size:11px}
        input:focus,select:focus{outline:none;border-color:#ff0000}
        .modal-actions{display:flex;gap:10px;margin-top:20px;justify-content:flex-end}
        .toast{position:fixed;top:20px;right:20px;padding:15px 25px;border:1px solid;z-index:9999;font-size:10px;letter-spacing:1px;display:none;animation:slideIn 0.3s ease}
        .toast-success{border-color:#0f0;color:#0f0;background:rgba(0,255,0,0.1)}
        .toast-error{border-color:#f00;color:#f00;background:rgba(255,0,0,0.1)}
        @keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
        .empty{text-align:center;color:#333;padding:30px;font-size:10px;letter-spacing:2px}
        .api-url{background:#000;padding:15px;border:1px solid rgba(255,0,0,0.1);font-size:10px;letter-spacing:1px;color:#0f0;overflow-x:auto;margin-top:10px;word-break:break-all}
        .action-btns{display:flex;gap:5px}
        .info-text{color:#666;font-size:10px;margin-top:10px}
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
        
        <!-- API Keys -->
        <div class="section">
            <div class="section-header">
                <h2>🔑 API KEYS</h2>
                <button class="btn" onclick="openModal('keyModal')">+ CREATE KEY</button>
            </div>
            {% if keys %}
            <table>
                <thead>
                    <tr><th>KEY</th><th>TYPE</th><th>STATUS</th><th>EXPIRES</th><th>TODAY</th><th>TOTAL</th><th>ACTIONS</th></tr>
                </thead>
                <tbody>
                    {% for key_name, key_data in keys.items() %}
                    <tr>
                        <td><code>{{ key_name if settings.show_keys else '••••••••' }}</code></td>
                        <td><span class="badge badge-vip">{{ key_data.type }}</span></td>
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
                    <tr><th>NAME</th><th>BASE URL</th><th>PARAM</th><th>FULL URL</th><th>STATUS</th><th>ACTIONS</th></tr>
                </thead>
                <tbody>
                    {% for api_name, api_data in apis.items() %}
                    <tr>
                        <td style="color:#ff0000">{{ api_data.name.upper() }}</td>
                        <td style="color:#888;font-size:9px;max-width:200px;overflow:hidden;text-overflow:ellipsis">{{ api_data.url }}</td>
                        <td><code>{{ api_data.params.keys()|list|first }}</code></td>
                        <td style="color:#0f0;font-size:9px;max-width:250px;overflow:hidden;text-overflow:ellipsis">{{ api_data.url }}?{{ api_data.params.keys()|list|first }}=VALUE</td>
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
            <div class="empty">NO APIs ADDED - CLICK "+ ADD API" TO ADD</div>
            {% endif %}
        </div>
        
        <!-- Usage -->
        <div class="section">
            <div class="section-header"><h2>📡 USAGE FORMAT</h2></div>
            <div class="api-url">{{ request.host_url }}api?key=KEY&api=API_NAME&PARAM=VALUE</div>
            <p class="info-text">Example: {{ request.host_url }}api?key=demo&api=rc&num=MH02FZ055</p>
            {% if apis %}
            <p class="info-text" style="color:#ff0000;margin-top:10px">Available APIs: {{ apis.keys()|list|join(', ') }}</p>
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
            <p style="color:#888;font-size:10px;margin-bottom:15px">⚠ ONLY ENTER BASE URL (without ? and parameters)</p>
            <form id="createApiForm">
                <label style="color:#888;font-size:10px">API NAME (short name like: rc, vehicle)</label>
                <input type="text" name="api_name" placeholder="e.g., rc" required>
                <label style="color:#888;font-size:10px">BASE URL (without ?param=)</label>
                <input type="text" name="api_url" placeholder="e.g., https://api.example.com/rc" required>
                <label style="color:#888;font-size:10px">PARAMETER KEY (e.g., num, vehicle, id)</label>
                <input type="text" name="param_key" placeholder="e.g., num" required>
                <label style="color:#888;font-size:10px">TIMEOUT (seconds)</label>
                <input type="number" name="timeout" placeholder="30" value="30" required>
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
            const d=await r.json();showToast('Key '+d.status,'success');
            setTimeout(()=>location.reload(),500);
        }
        async function deleteKey(name){
            if(confirm('DELETE: '+name+'?')){
                const r=await fetch('/admin/keys/delete/'+name,{method:'DELETE'});
                const d=await r.json();showToast(d.message,'success');
                setTimeout(()=>location.reload(),500);
            }
        }
        async function toggleApi(name){
            const r=await fetch('/admin/apis/toggle/'+name,{method:'POST'});
            const d=await r.json();showToast('API '+d.status,'success');
            setTimeout(()=>location.reload(),500);
        }
        async function deleteApi(name){
            if(confirm('DELETE: '+name+'?')){
                const r=await fetch('/admin/apis/delete/'+name,{method:'DELETE'});
                const d=await r.json();showToast(d.message,'success');
                setTimeout(()=>location.reload(),500);
            }
        }
    </script>
</body>
</html>
'''

# ==================== PUBLIC ROUTES ====================
@app.route('/')
def home():
    settings = load_json("settings.json")
    return jsonify({
        "server": "BRONX Ultra OSINT",
        "status": "ONLINE ✅",
        "owner": "@BRONX_ULTRA",
        "access": "RESTRICTED",
        "contact": "Contact @BRONX_ULTRA for API key"
    })

@app.route('/api')
def api_handler():
    valid, message, key_data = check_api_key()
    if not valid:
        return Response(json.dumps({"error": message}, indent=2), mimetype='application/json', status=401)
    
    api_name = request.args.get('api', '')
    apis = load_json("apis.json")
    
    print(f"[DEBUG] API Request - Key: valid, API: {api_name}, Available APIs: {list(apis.keys())}")
    
    if not api_name or api_name not in apis:
        return Response(json.dumps({
            "error": f"API '{api_name}' not found",
            "available_apis": list(apis.keys())
        }, indent=2), mimetype='application/json', status=404)
    
    api_config = apis[api_name]
    
    if api_config.get("status") != "active":
        return Response(json.dumps({"error": "API inactive"}, indent=2), mimetype='application/json', status=403)
    
    # Get parameter value
    param_value = None
    param_key = None
    for pk in api_config.get("params", {}).keys():
        param_key = pk
        param_value = request.args.get(pk)
        break
    
    if not param_value:
        return Response(json.dumps({
            "error": f"Parameter '{param_key}' required",
            "usage": f"/api?key=KEY&api={api_name}&{param_key}=VALUE"
        }, indent=2), mimetype='application/json', status=400)
    
    try:
        # Build URL - API URL already has base, we add params
        url = api_config["url"]
        params = {param_key: param_value}
        
        print(f"[DEBUG] Fetching: {url} with params: {params}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=api_config.get("timeout", 30), verify=False)
        
        print(f"[DEBUG] Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
            except:
                result = {"data": response.text}
        else:
            result = {"error": f"Upstream returned status {response.status_code}", "raw": response.text[:500]}
        
        # Add credit
        if isinstance(result, dict):
            result["_credit"] = "@BRONX_ULTRA"
        
        return Response(json.dumps(result, indent=2, ensure_ascii=False), mimetype='application/json; charset=utf-8')
        
    except requests.exceptions.Timeout:
        return Response(json.dumps({"error": "Upstream API timeout"}, indent=2), mimetype='application/json', status=504)
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
    api_name = request.form.get('api_name', '').strip().lower()
    api_url = request.form.get('api_url', '').strip().rstrip('/')
    param_key = request.form.get('param_key', '').strip()
    timeout = request.form.get('timeout', '30')
    
    # Remove ? and anything after from URL
    if '?' in api_url:
        api_url = api_url.split('?')[0]
    
    if not all([api_name, api_url, param_key]):
        return jsonify({"error": "All fields required"}), 400
    
    print(f"[DEBUG] Adding API - Name: {api_name}, URL: {api_url}, Param: {param_key}")
    
    apis = load_json("apis.json")
    if api_name in apis:
        return jsonify({"error": "API name already exists"}), 400
    
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
    print(f"[DEBUG] API Added Successfully: {api_name}")
    return jsonify({"success": True, "message": f"API '{api_name}' Added! Use: /api?key=KEY&api={api_name}&{param_key}=VALUE"})

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
    app.run(host='0.0.0.0', port=10000, debug=True)
