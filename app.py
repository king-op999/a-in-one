from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"

# ============ ALL APIs ============
BRONX_VEH2NUM_API = "https://bronx-web-api.onrender.com/api/key-bronx/veh2num"
LEAKAPI_VEHICLE = "https://leakapi.dpdns.org/api/vehicle"
LEAKAPI_REG = "https://leakapi.dpdns.org/vehicle-info"
UMMMYM_API = "https://ummmym.onrender.com/"

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ============ HOME PAGE ============
@app.route('/')
def home():
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🚗 BRONX RC API V8 - ALL IN ONE</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000a14;color:#d0d8f0;font-family:'Rajdhani',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(0,150,255,.06),transparent 60%),radial-gradient(ellipse at 80% 100%,rgba(139,0,255,.04),transparent 60%);pointer-events:none;z-index:0}}
.card{{background:rgba(5,15,35,.9);border:1px solid rgba(0,150,255,.1);border-radius:20px;padding:30px;max-width:700px;width:100%;text-align:center;position:relative;z-index:1;backdrop-filter:blur(20px)}}
h1{{font-family:'Orbitron',sans-serif;font-size:28px;background:linear-gradient(90deg,#0096ff,#00d4ff,#8b00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px}}
.badge{{display:inline-block;background:rgba(0,255,136,.06);color:#00ff88;padding:4px 14px;border-radius:20px;font-size:10px;border:1px solid rgba(0,255,136,.12);margin:4px}}
.section{{background:rgba(0,0,0,.5);border:1px solid rgba(0,150,255,.08);border-radius:12px;padding:16px;margin:14px 0;text-align:left}}
code{{color:#00ff88;font-family:monospace;font-size:11px;word-break:break-all;display:block;margin:6px 0;background:rgba(0,0,0,.3);padding:8px;border-radius:6px}}
input{{width:100%;padding:14px;background:rgba(0,0,0,.5);border:1px solid rgba(0,150,255,.08);border-radius:10px;color:#fff;font-size:14px;outline:none;margin:8px 0;font-family:'Rajdhani',sans-serif}}
input:focus{{border-color:#0096ff}}
button{{width:100%;padding:14px;background:linear-gradient(135deg,#0096ff,#0066cc);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-family:'Orbitron',sans-serif;font-size:14px;margin:6px 0;transition:.3s}}
button:hover{{transform:scale(1.02);box-shadow:0 0 25px rgba(0,150,255,.2)}}
.result{{background:rgba(0,0,0,.5);border:1px solid rgba(0,255,136,.08);border-radius:10px;padding:14px;margin-top:10px;text-align:left;display:none;max-height:600px;overflow:auto}}
.result.show{{display:block}}
pre{{color:#00ff88;font-family:monospace;font-size:10px;white-space:pre-wrap}}
</style></head>
<body>
<div class="card">
<h1>🚗 BRONX RC API V8</h1>
<p style="color:#667;font-size:12px">ALL-IN-ONE • LeakAPI • Veh2Num • UmmmyM • CarInfo</p>
<div style="margin:10px 0">
<span class="badge">👤 Owner</span><span class="badge">📱 Mobile</span><span class="badge">🚗 Vehicle</span><span class="badge">🏢 RTO</span><span class="badge">🛡️ Insurance</span>
</div>
<div class="section"><p style="color:#0096ff;font-weight:700">🔗 API Endpoint</p><code>GET /rc?num=MH02FZ0555</code></div>
<input type="text" id="rcInput" placeholder="RC Number (e.g., MH02FZ0555)">
<button onclick="lookup()">🔍 LOOKUP ALL SOURCES</button>
<div class="result" id="result"><pre id="resultData"></pre></div>
<p style="color:#667;font-size:10px;margin-top:14px">{CREDIT} | V8 ALL-IN-ONE</p>
</div>
<script>
async function lookup(){{
var n=document.getElementById('rcInput').value.trim();if(!n)return alert('Enter RC!');
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.style.color='#ffb400';p.textContent='🔍 Fetching from all sources...';
try{{var r=await fetch('/rc?num='+encodeURIComponent(n));var j=await r.json();p.style.color='#00ff88';p.textContent=JSON.stringify(j,null,2)}}catch(e){{p.style.color='#ff3366';p.textContent='❌ '+e.message}}}}
</script>
</body></html>'''

# ============ SOURCE 1: LeakAPI /api/vehicle ============
def get_leakapi_vehicle(rc_number):
    try:
        url = f"{LEAKAPI_VEHICLE}?vehicle={rc_number}"
        resp = requests.get(url, timeout=25)
        data = resp.json()
        if data:
            if isinstance(data, dict) and '_proxy' in data:
                del data['_proxy']
            return data
        return None
    except:
        return None

# ============ SOURCE 2: LeakAPI /vehicle-info ============
def get_leakapi_reg(rc_number):
    try:
        url = f"{LEAKAPI_REG}?registration_number={rc_number}"
        resp = requests.get(url, timeout=25)
        data = resp.json()
        if data:
            if isinstance(data, dict) and '_proxy' in data:
                del data['_proxy']
            return data
        return None
    except:
        return None

# ============ SOURCE 3: Bronx Veh2Num (Mobile) ============
def get_bronx_veh2num(rc_number):
    try:
        url = f"{BRONX_VEH2NUM_API}?key=op&vehicle={rc_number}"
        resp = requests.get(url, timeout=20)
        data = resp.json()
        if isinstance(data, dict) and '_proxy' in data:
            del data['_proxy']
        
        if data and data.get('mobile_number'):
            return data.get('mobile_number')
        if data and isinstance(data, dict):
            for key in ['mobile_number', 'mobile', 'phone', 'number', 'owner_number', 'result']:
                if data.get(key):
                    val = data[key]
                    if isinstance(val, str) and val.isdigit() and len(val) == 10:
                        return val
                    elif isinstance(val, dict):
                        for k in ['mobile', 'phone', 'number']:
                            if val.get(k):
                                return str(val[k])
        return None
    except:
        return None

# ============ SOURCE 4: UmmmyM (SLOW - 30 sec timeout) ============
def get_ummym_data(rc_number):
    try:
        url = f"{UMMMYM_API}?rc={rc_number}"
        resp = requests.get(url, timeout=35)
        data = resp.json()
        if data:
            if isinstance(data, dict) and '_proxy' in data:
                del data['_proxy']
            if isinstance(data, dict):
                for key in list(data.keys()):
                    if isinstance(data[key], dict) and '_proxy' in data[key]:
                        del data[key]['_proxy']
            return data
        return None
    except:
        return None

# ============ SOURCE 5: VahanX Scraper ============
def get_vahanx_data(rc_number):
    url = f"https://vahanx.in/rc-search/{rc_number}"
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        
        def gv(label):
            try:
                span = soup.find("span", string=label)
                if span:
                    div = span.find_parent("div")
                    if div:
                        p = div.find("p")
                        if p:
                            return p.get_text(strip=True)
                return None
            except:
                return None
        
        father = gv("Father's Name")
        if not father:
            so = re.search(r'(S/O|D/O|W/O)\s*SH\.?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
            if so:
                father = f"{so.group(1)} SH. {so.group(2).strip()}"
        
        return {
            "father_name": father,
            "owner_name": gv("Owner Name"),
            "phone": gv("Phone"),
            "address": gv("Address"),
            "city": gv("City Name"),
            "rto": gv("Registered RTO"),
            "reg_date": gv("Registration Date"),
            "model": gv("Model Name"),
            "fuel": gv("Fuel Type"),
            "insurance_company": gv("Insurance Company"),
            "insurance_upto": gv("Insurance Upto"),
            "fitness_upto": gv("Fitness Upto"),
            "tax_upto": gv("Tax Upto"),
            "puc_upto": gv("PUC Upto"),
        }
    except:
        return {}

# ============ SOURCE 6: CarInfo RTO ============
def get_carinfo_rto(rc_number):
    url = f"https://www.carinfo.app/rto-vehicle-registration-detail/rto-details/{rc_number}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        info = {}
        match = re.match(r'^([A-Z]{2}\d{2})', rc_number)
        if match:
            info["rto_code"] = match.group(1)
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    k = cells[0].get_text(strip=True).lower()
                    v = cells[1].get_text(strip=True)
                    if 'state' in k:
                        info['state'] = v
                    elif 'address' in k:
                        info['rto_address'] = v
                    elif 'phone' in k:
                        info['rto_phone'] = v
                    elif 'email' in k:
                        info['rto_email'] = v
                    elif 'city' in k:
                        info['rto_city'] = v
        return info if len(info) > 1 else None
    except:
        return None

# ============ MAIN RC ENDPOINT ============
@app.route('/rc')
def rc_lookup():
    start_time = time.time()
    rc_number = request.args.get('num', '').strip().upper().replace(' ', '').replace('-', '')
    
    if not rc_number:
        return jsonify({
            "status": "error",
            "message": "Missing RC number",
            "credit": CREDIT
        }), 400
    
    # PARALLEL FETCHING
    results = {}
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(get_leakapi_vehicle, rc_number): 'leakapi_vehicle',
            executor.submit(get_leakapi_reg, rc_number): 'leakapi_registration',
            executor.submit(get_bronx_veh2num, rc_number): 'veh2num_mobile',
            executor.submit(get_ummym_data, rc_number): 'ummym',
            executor.submit(get_vahanx_data, rc_number): 'vahanx',
            executor.submit(get_carinfo_rto, rc_number): 'carinfo_rto',
        }
        
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                results[source_name] = future.result(timeout=40)
            except:
                results[source_name] = None
    
    leakapi_v = results.get('leakapi_vehicle')
    leakapi_r = results.get('leakapi_registration')
    v2n = results.get('veh2num_mobile')
    ummym = results.get('ummym')
    vx = results.get('vahanx')
    rto = results.get('carinfo_rto')
    
    response_time = round(time.time() - start_time, 2)
    
    result = {
        "status": "success",
        "rc_number": rc_number,
        "credit": CREDIT,
        "powered_by": "@BRONX_ULTRA",
        "response_time_seconds": response_time,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "sources": {
            "leakapi_vehicle": "✅" if leakapi_v else "❌",
            "leakapi_registration": "✅" if leakapi_r else "❌",
            "veh2num_mobile": "✅" if v2n else "❌",
            "ummym": "✅" if ummym else "❌",
            "vahanx_scraper": "✅" if vx else "❌",
            "carinfo_rto": "✅" if rto else "❌"
        }
    }
    
    if leakapi_v:
        result["leakapi_vehicle"] = leakapi_v
    
    if leakapi_r:
        result["leakapi_registration"] = leakapi_r
    
    if ummym:
        result["ummym"] = ummym
    
    if v2n:
        result["mobile_number"] = v2n
    
    if vx:
        vx_clean = {k: v for k, v in vx.items() if v}
        if vx_clean:
            result["vahanx_scraper"] = vx_clean
    
    if rto:
        result["carinfo_rto"] = rto
    
    # MERGED SUMMARY
    owner_name = "N/A"
    model = "N/A"
    fuel = "N/A"
    reg_date = "N/A"
    rto_name = "N/A"
    
    if leakapi_v and isinstance(leakapi_v, dict):
        owner_name = leakapi_v.get('owner_name') or leakapi_v.get('owner') or owner_name
        model = leakapi_v.get('model') or leakapi_v.get('vehicle_model') or model
        fuel = leakapi_v.get('fuel') or leakapi_v.get('fuel_type') or fuel
        reg_date = leakapi_v.get('registration_date') or leakapi_v.get('reg_date') or reg_date
        rto_name = leakapi_v.get('rto') or leakapi_v.get('rto_name') or rto_name
    
    if ummym and isinstance(ummym, dict):
        owner_name = ummym.get('owner_name') or ummym.get('owner') or owner_name
        model = ummym.get('model') or ummym.get('vehicle_model') or model
        fuel = ummym.get('fuel') or ummym.get('fuel_type') or fuel
    
    if vx:
        owner_name = vx.get('owner_name') or owner_name
        model = vx.get('model') or model
        fuel = vx.get('fuel') or fuel
        reg_date = vx.get('reg_date') or reg_date
        rto_name = vx.get('rto') or rto_name
    
    result["📋_summary"] = {
        "owner_name": owner_name,
        "mobile_number": v2n or "N/A",
        "model": model,
        "fuel_type": fuel,
        "registration_date": reg_date,
        "rto_name": rto_name
    }
    
    return jsonify(result)


# ============ HEALTH CHECK ============
@app.route('/health')
@app.route('/test')
def test():
    return jsonify({
        "status": "✅ BRONX RC API V8 ONLINE",
        "version": "8.0 ALL-IN-ONE",
        "endpoint": "/rc?num=MH02FZ0555",
        "sources": [
            "1",
            "2",
            "Veh2Num Mobile",
            "3",
            "4",
            "5"
        ],
        "credit": "@BRONX_ULTRA"
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "home": "/",
        "api": "/rc?num=RC_NUMBER"
    }), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
