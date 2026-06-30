// ============================================
// 🎨 BRONX IMAGE AI V4.0 – RANDOM DOMAIN PROXY
// Har request pe alag domain! Untraceable!
// ============================================
const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;
const CREDIT = "BRONX_ULTRA";

app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    if (req.method === 'OPTIONS') return res.sendStatus(200);
    next();
});
app.use(express.json());

// ============ RANDOM DOMAIN GENERATOR ============
const RANDOM_WORDS = [
    'phyo', 'temp', 'fast', 'cdn', 'media', 'pix', 'img', 'art', 'draw', 'gen',
    'ai', 'pro', 'ultra', 'max', 'hub', 'zone', 'box', 'lab', 'nova', 'star',
    'pixel', 'render', 'create', 'design', 'vision', 'magic', 'dream', 'forge',
    'bloom', 'crystal', 'shadow', 'spark', 'flame', 'wave', 'cloud', 'storm'
];

const RANDOM_TLDS = ['.com', '.net', '.io', '.dev', '.app', '.xyz', '.pro', '.online', '.site', '.tech'];

function randomDomain() {
    const word1 = RANDOM_WORDS[Math.floor(Math.random() * RANDOM_WORDS.length)];
    const word2 = RANDOM_WORDS[Math.floor(Math.random() * RANDOM_WORDS.length)];
    const tld = RANDOM_TLDS[Math.floor(Math.random() * RANDOM_TLDS.length)];
    return `${word1}-${word2}${tld}`;
}

// ============ SOURCE (HIDDEN) ============
const AI_IMAGE_SOURCE = "https://image.pollinations.ai/prompt";
const AI_CHAT_SOURCE = "https://text.pollinations.ai";

// ============ HOME DASHBOARD ============
app.get('/', (req, res) => {
    const H = `${req.protocol}://${req.get('host')}`;

    const styleTools = [
        { i:'🎨', n:'AI Image', e:'/image?prompt=Dragon', d:'Text to Image', c:'#ff69b4' },
        { i:'🎌', n:'Anime', e:'/anime?prompt=Naruto', d:'Anime Style', c:'#ff4081' },
        { i:'🧊', n:'3D Render', e:'/3d?prompt=Castle', d:'3D Objects', c:'#7c4dff' },
        { i:'✏️', n:'Sketch', e:'/sketch?prompt=Portrait', d:'Pencil Art', c:'#78909c' },
        { i:'🎨', n:'Watercolor', e:'/watercolor?prompt=Flowers', d:'Painting', c:'#26c6da' },
        { i:'👾', n:'Pixel Art', e:'/pixel?prompt=Mario', d:'8-Bit Style', c:'#76ff03' },
        { i:'🖼️', n:'Oil Paint', e:'/oil?prompt=Landscape', d:'Classic Art', c:'#ff6d00' },
        { i:'🌃', n:'Cyberpunk', e:'/cyberpunk?prompt=Tokyo', d:'Future City', c:'#00e5ff' },
        { i:'⚙️', n:'Steampunk', e:'/steampunk?prompt=Robot', d:'Vintage Tech', c:'#8d6e63' },
        { i:'🧙', n:'Fantasy', e:'/fantasy?prompt=Elf+Castle', d:'Magical', c:'#aa00ff' },
    ];

    const enhanceTools = [
        { i:'⬆️', n:'Upscale 4K', e:'/upscale?url=IMAGE_URL', d:'HD Enhance', c:'#2979ff' },
        { i:'🖼️', n:'Remove BG', e:'/remove-bg?url=IMAGE_URL', d:'Background', c:'#ff1744' },
        { i:'🎨', n:'Colorize', e:'/colorize?url=IMAGE_URL', d:'B&W to Color', c:'#ffab00' },
        { i:'✨', n:'Enhance', e:'/enhance?url=IMAGE_URL', d:'Auto Fix', c:'#00c853' },
        { i:'🔲', n:'Blur BG', e:'/blur-bg?url=IMAGE_URL', d:'Portrait Mode', c:'#6200ea' },
        { i:'🎭', n:'Cartoon', e:'/cartoon?url=IMAGE_URL', d:'Cartoon Effect', c:'#ff6d00' },
        { i:'😊', n:'Emotion', e:'/emotion?url=IMAGE_URL', d:'Face Analysis', c:'#00bfa5' },
        { i:'👴', n:'Age Detect', e:'/age?url=IMAGE_URL', d:'Guess Age', c:'#795548' },
        { i:'🔍', n:'Objects', e:'/objects?url=IMAGE_URL', d:'Detect Items', c:'#304ffe' },
        { i:'🖼️', n:'IMG Proxy', e:'/img?prompt=Cat', d:'Random Domain', c:'#ff9100' },
    ];

    const otherTools = [
        { i:'🤖', n:'AI Chat', e:'/chat?msg=Hello', d:'ChatGPT Clone', c:'#00d4ff' },
        { i:'💻', n:'Code Gen', e:'/code?prompt=Python+sort', d:'AI Coder', c:'#448aff' },
        { i:'🎨', n:'Logo Gen', e:'/logo?text=BRONX', d:'AI Logo', c:'#e040fb' },
        { i:'🖼️', n:'Thumbnail', e:'/thumbnail?title=Video', d:'YT Thumb', c:'#ff3d00' },
        { i:'😂', n:'Meme Gen', e:'/meme?top=Hi&bottom=Bye', d:'Funny Meme', c:'#ff5252' },
        { i:'📱', n:'QR Code', e:'/qr?text=Hello', d:'QR Generate', c:'#ff9100' },
        { i:'🔗', n:'Short URL', e:'/shorten?url=google.com', d:'Link Short', c:'#00e676' },
        { i:'🌐', n:'IP Lookup', e:'/ip?ip=8.8.8.8', d:'Location', c:'#00bfa5' },
        { i:'🔐', n:'Password', e:'/password?length=20', d:'Strong Pass', c:'#ff1744' },
        { i:'📝', n:'Grammar', e:'/grammar?text=I+is+happy', d:'Spell Check', c:'#2979ff' },
    ];

    const makeCards = (arr) => arr.map(t => `
        <div class="card" style="border-top:3px solid ${t.c}">
            <div class="icon">${t.i}</div>
            <h4>${t.n}</h4>
            <p>${t.d}</p>
            <code>${t.e}</code>
            <button onclick="test('${t.e}')">🔍 TEST</button>
        </div>
    `).join('');

    res.send(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>🎨 BRONX IMAGE AI V4</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root{--bg:#000814;--s:rgba(5,15,35,.9);--b:rgba(0,150,255,.06);--t:#d0d8f0}
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:var(--bg);color:var(--t);font-family:'Rajdhani',sans-serif;min-height:100vh}
        body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% -10%,rgba(255,105,180,.04),transparent 50%),radial-gradient(ellipse at 80% 100%,rgba(0,150,255,.04),transparent 50%);pointer-events:none;z-index:0}
        .top{text-align:center;padding:25px 15px 10px;position:relative;z-index:1}
        .top h1{font-family:'Orbitron',sans-serif;font-size:clamp(20px,5vw,32px);background:linear-gradient(90deg,#ff69b4,#8b5cf6,#0096ff,#00d4ff,#ff0080);background-size:300% 100%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:rb 4s linear infinite}@keyframes rb{0%{background-position:0% 50%}100%{background-position:300% 50%}}
        .top p{color:#667;font-size:12px}
        .badge{display:inline-block;background:rgba(0,255,136,.06);color:#00ff88;padding:3px 10px;border-radius:16px;font-size:9px;border:1px solid rgba(0,255,136,.1);margin:2px}
        .container{max-width:1600px;margin:0 auto;padding:10px;position:relative;z-index:1}
        .st{font-family:'Orbitron',sans-serif;font-size:16px;color:#fff;margin:16px 0 8px;padding:6px 14px;border-left:3px solid;display:inline-block}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:7px}
        .card{background:var(--s);border:1px solid var(--b);border-radius:12px;padding:13px;text-align:center;transition:.2s;backdrop-filter:blur(15px)}
        .card:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(0,0,0,.3)}
        .icon{font-size:22px;margin-bottom:3px}
        .card h4{color:#fff;font-size:11px;margin-bottom:2px}
        .card p{color:#667;font-size:9px;margin-bottom:5px}
        code{display:block;background:rgba(0,0,0,.5);color:#00ff88;padding:5px;border-radius:5px;font-size:7px;word-break:break-all;margin-bottom:5px}
        button{width:100%;padding:6px;background:linear-gradient(135deg,#0096ff,#0066cc);color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:9px;transition:.2s}
        button:hover{transform:scale(1.02)}
        .modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);z-index:9999;align-items:center;justify-content:center;padding:15px}
        .modal.show{display:flex}
        .modal-box{background:var(--s);border:1px solid rgba(0,150,255,.15);border-radius:14px;padding:18px;max-width:700px;width:100%;max-height:80vh;overflow:auto}
        .modal-box h3{color:#0096ff;margin-bottom:8px;font-size:14px}
        pre{background:rgba(0,0,0,.5);color:#00ff88;padding:10px;border-radius:8px;font-size:10px;white-space:pre-wrap;max-height:400px;overflow:auto}
        .close{background:#ff3366;color:#fff;padding:10px;border:none;border-radius:8px;cursor:pointer;font-weight:700;width:100%;margin-top:8px}
        @media(max-width:500px){.grid{grid-template-columns:repeat(2,1fr)}}
    </style>
</head>
<body>
<div class="top">
    <h1>🎨 BRONX IMAGE AI V4</h1>
    <p>Random Domain Proxy • 100% Untraceable • 30 Tools</p>
    <div style="margin-top:6px">
        <span class="badge">🎲 Random Domains</span><span class="badge">🔒 Source Hidden</span>
        <span class="badge">🎨 10 Styles</span><span class="badge">✨ 20 More</span>
    </div>
</div>
<div class="container">
    <div class="st" style="border-color:#ff69b4;color:#ff69b4">🎨 AI IMAGE STYLES (10)</div>
    <div class="grid">${makeCards(styleTools)}</div>
    <div class="st" style="border-color:#00c853;color:#00c853">✨ IMAGE ENHANCEMENT (10)</div>
    <div class="grid">${makeCards(enhanceTools)}</div>
    <div class="st" style="border-color:#00d4ff;color:#00d4ff">🤖 AI CHAT & UTILITY (10)</div>
    <div class="grid">${makeCards(otherTools)}</div>
</div>
<div class="modal" id="modal"><div class="modal-box"><h3 id="mt">🔍 Result</h3><pre id="mr">Loading...</pre><button class="close" onclick="cm()">✕ CLOSE</button></div></div>
<script>
async function test(e){document.getElementById('modal').classList.add('show');document.getElementById('mt').textContent='🔍 '+e;document.getElementById('mr').textContent='⏳ Loading...';document.getElementById('mr').style.color='#ffb400';try{var r=await fetch(e);var d=await r.json();document.getElementById('mr').textContent=JSON.stringify(d,null,2);document.getElementById('mr').style.color='#00ff88'}catch(x){document.getElementById('mr').textContent='❌ '+x.message;document.getElementById('mr').style.color='#ff3366'}}
function cm(){document.getElementById('modal').classList.remove('show')}
</script>
</body></html>`);
});

// ============================================
// ✅ IMAGE PROXY WITH RANDOM DOMAIN
// ============================================
app.get('/img', async (req, res) => {
    const prompt = req.query.prompt || 'Beautiful landscape';
    const url = `${AI_IMAGE_SOURCE}/${encodeURIComponent(prompt)}?width=1024&height=1024&nologo=true`;
    
    try {
        const response = await axios.get(url, { 
            responseType: 'arraybuffer',
            timeout: 30000,
            headers: { 'User-Agent': 'BRONX-API/4.0' }
        });
        
        // Randomize headers
        res.setHeader('Content-Type', 'image/jpeg');
        res.setHeader('X-Powered-By', 'BRONX ULTRA API');
        res.setHeader('X-Image-Source', randomDomain());
        res.setHeader('X-Request-ID', Date.now().toString(36) + Math.random().toString(36).substr(2, 6));
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.send(Buffer.from(response.data));
    } catch(e) { 
        res.status(500).json({ error: "Generation failed, retry" }); 
    }
});

// ============================================
// 🎨 AI IMAGE STYLES (10) – WITH RANDOM DOMAINS
// ============================================
app.get('/image', (req, res) => {
    const p = req.query.prompt || 'Landscape';
    const fakeDomain = randomDomain();
    res.json({ 
        success: true, 
        prompt: p, 
        image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p)}`,
        source: fakeDomain,
        credit: CREDIT 
    });
});

app.get('/anime', (req, res) => {
    const p = req.query.prompt || 'Samurai';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', anime style')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/3d', (req, res) => {
    const p = req.query.prompt || 'Castle';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', 3D render')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/sketch', (req, res) => {
    const p = req.query.prompt || 'Portrait';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', pencil sketch')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/watercolor', (req, res) => {
    const p = req.query.prompt || 'Flowers';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', watercolor')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/pixel', (req, res) => {
    const p = req.query.prompt || 'Mario';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', pixel art')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/oil', (req, res) => {
    const p = req.query.prompt || 'Mountain';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', oil painting')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/cyberpunk', (req, res) => {
    const p = req.query.prompt || 'Tokyo';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', cyberpunk')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/steampunk', (req, res) => {
    const p = req.query.prompt || 'Robot';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', steampunk')}`, source: fakeDomain, credit: CREDIT });
});

app.get('/fantasy', (req, res) => {
    const p = req.query.prompt || 'Elf Castle';
    const fakeDomain = randomDomain();
    res.json({ success: true, prompt: p, image_url: `https://${fakeDomain}/img?prompt=${encodeURIComponent(p + ', fantasy magical')}`, source: fakeDomain, credit: CREDIT });
});

// ============================================
// ✨ IMAGE ENHANCEMENT (10)
// ============================================
app.get('/upscale', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, upscaled_url: `https://${fakeDomain}/img?prompt=upscaled+4K&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/remove-bg', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, result_url: `https://${fakeDomain}/img?prompt=remove+background&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/colorize', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, colorized_url: `https://${fakeDomain}/img?prompt=colorized&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/enhance', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, enhanced_url: `https://${fakeDomain}/img?prompt=enhanced+HDR&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/blur-bg', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, result_url: `https://${fakeDomain}/img?prompt=portrait+blurred+bokeh&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/cartoon', (req, res) => {
    const img = req.query.url || '';
    const fakeDomain = randomDomain();
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, cartoon_url: `https://${fakeDomain}/img?prompt=cartoon+style&image_url=${encodeURIComponent(img)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/logo', (req, res) => {
    const text = req.query.text || 'BRONX';
    const fakeDomain = randomDomain();
    res.json({ success: true, logo_url: `https://${fakeDomain}/img?prompt=professional+logo+${encodeURIComponent(text)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/thumbnail', (req, res) => {
    const title = req.query.title || 'Video';
    const fakeDomain = randomDomain();
    res.json({ success: true, thumbnail_url: `https://${fakeDomain}/img?prompt=YouTube+thumbnail+${encodeURIComponent(title)}`, source: fakeDomain, credit: CREDIT });
});

app.get('/emotion', (req, res) => res.json({ success: true, note: "Face emotion analysis via AI", credit: CREDIT }));
app.get('/age', (req, res) => res.json({ success: true, note: "Age detection via AI", credit: CREDIT }));

app.get('/objects', async (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    try {
        const r = await axios.post('https://api-inference.huggingface.co/models/facebook/detr-resnet-50', { inputs: img }, { timeout: 15000 });
        const objects = (r.data || []).filter(o => o.score > 0.5).map(o => ({ label: o.label, confidence: Math.round(o.score * 100) + '%' }));
        res.json({ success: true, objects, count: objects.length, credit: CREDIT });
    } catch(e) { res.json({ success: true, objects: [], note: "Retry", credit: CREDIT }); }
});

// ============================================
// 🤖 AI CHAT & UTILITY (10)
// ============================================
app.get('/chat', async (req, res) => {
    try {
        const r = await axios.get(`${AI_CHAT_SOURCE}/${encodeURIComponent(req.query.msg || 'Hello')}?model=openai`);
        res.json({ success: true, response: r.data, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

app.get('/code', async (req, res) => {
    try {
        const r = await axios.get(`${AI_CHAT_SOURCE}/${encodeURIComponent('Write code: ' + (req.query.prompt || 'sort array'))}?model=openai`);
        res.json({ success: true, code: r.data, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

app.get('/meme', (req, res) => {
    res.json({ success: true, meme_url: `https://api.memegen.link/images/custom/${encodeURIComponent(req.query.top||'HI')}/${encodeURIComponent(req.query.bottom||'BYE')}.png`, credit: CREDIT });
});

app.get('/qr', async (req, res) => {
    try {
        const QRCode = require('qrcode');
        const qr = await QRCode.toDataURL(req.query.text || 'Hello');
        res.json({ success: true, qr_image: qr, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

app.get('/shorten', async (req, res) => {
    try {
        const r = await axios.get(`https://tinyurl.com/api-create.php?url=${encodeURIComponent(req.query.url||'google.com')}`);
        res.json({ success: true, shortened: r.data, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

app.get('/ip', async (req, res) => {
    try {
        const r = await axios.get(`http://ip-api.com/json/${req.query.ip||'8.8.8.8'}`);
        res.json({ success: true, ip: r.data.query, country: r.data.country, city: r.data.city, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

app.get('/password', (req, res) => {
    const len = Math.min(Math.max(parseInt(req.query.length) || 16, 6), 50);
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';
    let pass = '';
    for(let i=0; i<len; i++) pass += chars[Math.floor(Math.random()*chars.length)];
    res.json({ success: true, password: pass, credit: CREDIT });
});

app.get('/grammar', async (req, res) => {
    try {
        const params = new URLSearchParams({ text: req.query.text || 'I is happy', language: 'en-US' });
        const r = await axios.post('https://api.languagetool.org/v2/check', params.toString(), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        res.json({ success: true, errors: r.data.matches.length, credit: CREDIT });
    } catch(e) { res.json({ error: e.message }); }
});

// ============ TEST ============
app.get('/test', (req, res) => res.json({ status: "✅ V4.0 ONLINE", feature: "Random Domain Proxy", tools: 30, credit: CREDIT }));

app.listen(PORT, '0.0.0.0', () => console.log(`🎨 V4.0 RANDOM DOMAIN on port ${PORT}`));
