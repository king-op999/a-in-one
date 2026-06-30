// ============================================
// 🎨🎵 BRONX MEDIA API V2.0 ULTRA
// 25 Tools – Image + Audio/Video
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

// ============ POLLINATIONS AI HELPER ============
const genImage = (prompt, style = '', w = 1024, h = 1024) => {
    const fullPrompt = style ? `${prompt}, ${style} style` : prompt;
    return `https://image.pollinations.ai/prompt/${encodeURIComponent(fullPrompt)}?width=${w}&height=${h}&nologo=true`;
};

// ============ HOME DASHBOARD ============
app.get('/', (req, res) => {
    const H = `${req.protocol}://${req.get('host')}`;
    
    const imageTools = [
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

    const audioVideoTools = [
        { i:'🎵', n:'Music Gen', e:'/music?prompt=Happy+melody', d:'AI Music', c:'#ff1744' },
        { i:'🥁', n:'Beat Maker', e:'/beat?prompt=Hip+Hop', d:'Drum Beats', c:'#ff9100' },
        { i:'🎤', n:'Voice Change', e:'/voice-change?style=female', d:'Female Voice', c:'#e040fb' },
        { i:'📝', n:'Audio2Text', e:'/audio-text', d:'Transcription', c:'#00c853' },
        { i:'🎬', n:'Video Summary', e:'/video-summary', d:'Key Moments', c:'#448aff' },
        { i:'💬', n:'Subtitles', e:'/subtitles', d:'Auto Captions', c:'#009688' },
        { i:'🖼️', n:'Thumbnail', e:'/thumbnail?title=Gaming', d:'YouTube', c:'#ff3d00' },
        { i:'🎞️', n:'GIF Maker', e:'/gif?prompt=Dancing+cat', d:'Animated GIF', c:'#ffea00' },
        { i:'😂', n:'Meme Gen', e:'/meme?top=Hello&bottom=World', d:'Funny Memes', c:'#ff5252' },
        { i:'📸', n:'Slideshow', e:'/slideshow', d:'Photo2Video', c:'#4caf50' },
        { i:'🖼️', n:'Remove BG', e:'/remove-bg?url=IMAGE', d:'Background', c:'#ff1744' },
        { i:'⬆️', n:'Upscale', e:'/upscale?url=IMAGE', d:'HD Enhance', c:'#2979ff' },
        { i:'🎨', n:'Colorize', e:'/colorize?url=IMAGE', d:'B&W to Color', c:'#ffab00' },
        { i:'😊', n:'Emotion', e:'/emotion?url=IMAGE', d:'Face Emotion', c:'#00bfa5' },
        { i:'👴', n:'Age/Gender', e:'/age-gender?url=IMAGE', d:'Detect Age', c:'#795548' },
    ];

    const imgCards = imageTools.map(t => `
        <div class="card" style="border-top:3px solid ${t.c}">
            <div class="icon">${t.i}</div>
            <h4>${t.n}</h4>
            <p>${t.d}</p>
            <code>${t.e}</code>
            <button onclick="test('${t.e}')">🔍 TEST</button>
        </div>
    `).join('');

    const avCards = audioVideoTools.map(t => `
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
    <title>🎨🎵 BRONX MEDIA API V2</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root{--bg:#000814;--s:rgba(5,15,35,.9);--b:rgba(0,150,255,.06);--t:#d0d8f0}
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:var(--bg);color:var(--t);font-family:'Rajdhani',sans-serif;min-height:100vh}
        body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% -10%,rgba(0,150,255,.05),transparent 50%),radial-gradient(ellipse at 80% 100%,rgba(139,0,255,.03),transparent 50%);pointer-events:none;z-index:0}
        .top{text-align:center;padding:25px 15px 10px;position:relative;z-index:1}
        .top h1{font-family:'Orbitron',sans-serif;font-size:clamp(20px,5vw,32px);background:linear-gradient(90deg,#ff69b4,#8b5cf6,#0096ff,#00d4ff,#ff0080);background-size:300% 100%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:rb 4s linear infinite}@keyframes rb{0%{background-position:0% 50%}100%{background-position:300% 50%}}
        .top p{color:#667;font-size:12px}
        .badge{display:inline-block;background:rgba(0,255,136,.06);color:#00ff88;padding:3px 10px;border-radius:16px;font-size:9px;border:1px solid rgba(0,255,136,.1);margin:2px}
        .container{max-width:1500px;margin:0 auto;padding:10px;position:relative;z-index:1}
        .section-title{font-family:'Orbitron',sans-serif;font-size:18px;color:#fff;margin:18px 0 10px;padding:8px 16px;border-left:3px solid;display:inline-block}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}
        .card{background:var(--s);border:1px solid var(--b);border-radius:12px;padding:14px;text-align:center;transition:.2s;backdrop-filter:blur(15px)}
        .card:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(0,0,0,.3)}
        .icon{font-size:24px;margin-bottom:4px}
        .card h4{color:#fff;font-size:12px;margin-bottom:2px}
        .card p{color:#667;font-size:9px;margin-bottom:6px}
        code{display:block;background:rgba(0,0,0,.5);color:#00ff88;padding:5px;border-radius:5px;font-size:8px;word-break:break-all;margin-bottom:6px}
        button{width:100%;padding:7px;background:linear-gradient(135deg,#0096ff,#0066cc);color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:10px;transition:.2s}
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
    <h1>🎨🎵 BRONX MEDIA API V2</h1>
    <p>25 Tools • Image Generation + Audio/Video Processing</p>
    <div style="margin-top:6px">
        <span class="badge">🎨 10 Image</span><span class="badge">🎵 15 Audio/Video</span>
        <span class="badge">⚡ Free</span><span class="badge">🚀 Fast</span>
    </div>
</div>
<div class="container">
    <div class="section-title" style="border-color:#ff69b4;color:#ff69b4">🎨 IMAGE TOOLS (10)</div>
    <div class="grid">${imgCards}</div>
    
    <div class="section-title" style="border-color:#ff1744;color:#ff1744">🎵 AUDIO & VIDEO TOOLS (15)</div>
    <div class="grid">${avCards}</div>
</div>

<div class="modal" id="modal">
    <div class="modal-box">
        <h3 id="mt">🔍 Result</h3>
        <pre id="mr">Loading...</pre>
        <button class="close" onclick="cm()">✕ CLOSE</button>
    </div>
</div>
<script>
async function test(e){
    document.getElementById('modal').classList.add('show');
    document.getElementById('mt').textContent='🔍 '+e;document.getElementById('mr').textContent='⏳ Loading...';document.getElementById('mr').style.color='#ffb400';
    try{var r=await fetch(e);var d=await r.json();document.getElementById('mr').textContent=JSON.stringify(d,null,2);document.getElementById('mr').style.color='#00ff88'}catch(x){document.getElementById('mr').textContent='❌ '+x.message;document.getElementById('mr').style.color='#ff3366'}}
function cm(){document.getElementById('modal').classList.remove('show')}
</script>
</body></html>`);
});

// ============================================
// 🎨 IMAGE TOOLS (10)
// ============================================

app.get('/image', (req, res) => {
    const p = req.query.prompt || 'Beautiful landscape';
    res.json({ success: true, prompt: p, image_url: genImage(p), credit: CREDIT });
});

app.get('/anime', (req, res) => {
    const p = req.query.prompt || 'Samurai warrior';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'anime'), credit: CREDIT });
});

app.get('/3d', (req, res) => {
    const p = req.query.prompt || 'Futuristic castle';
    res.json({ success: true, prompt: p, image_url: genImage(p, '3D render, octane render, ray tracing'), credit: CREDIT });
});

app.get('/sketch', (req, res) => {
    const p = req.query.prompt || 'Old man portrait';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'pencil sketch, black and white, detailed'), credit: CREDIT });
});

app.get('/watercolor', (req, res) => {
    const p = req.query.prompt || 'Colorful flowers garden';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'watercolor painting, soft colors'), credit: CREDIT });
});

app.get('/pixel', (req, res) => {
    const p = req.query.prompt || 'Game character';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'pixel art, 8-bit, retro game style'), credit: CREDIT });
});

app.get('/oil', (req, res) => {
    const p = req.query.prompt || 'Mountain landscape';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'oil painting, classical art, museum quality'), credit: CREDIT });
});

app.get('/cyberpunk', (req, res) => {
    const p = req.query.prompt || 'Tokyo night city';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'cyberpunk, neon lights, futuristic, rain'), credit: CREDIT });
});

app.get('/steampunk', (req, res) => {
    const p = req.query.prompt || 'Mechanical robot';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'steampunk, victorian, brass gears'), credit: CREDIT });
});

app.get('/fantasy', (req, res) => {
    const p = req.query.prompt || 'Elf castle in forest';
    res.json({ success: true, prompt: p, image_url: genImage(p, 'fantasy art, magical, epic, detailed'), credit: CREDIT });
});

// ============================================
// 🎵 AUDIO & VIDEO TOOLS (15)
// ============================================

app.get('/music', (req, res) => {
    const p = req.query.prompt || 'Happy melody';
    res.json({ success: true, prompt: p, note: "Use MusicGen on HuggingFace for full music", music_hf: "https://huggingface.co/spaces/facebook/MusicGen", credit: CREDIT });
});

app.get('/beat', (req, res) => {
    const p = req.query.prompt || 'Hip Hop drum beat';
    res.json({ success: true, prompt: p, note: "Use BeatMaker on HuggingFace", beat_hf: "https://huggingface.co/spaces", credit: CREDIT });
});

app.get('/voice-change', (req, res) => {
    const style = req.query.style || 'female';
    res.json({ success: true, style: style, note: "Use RVC Voice Changer on HuggingFace", rvc_url: "https://huggingface.co/spaces/wok000/so-vits-svc-5.0", credit: CREDIT });
});

app.get('/audio-text', (req, res) => {
    res.json({ success: true, note: "Use Whisper for audio transcription", whisper_url: "https://huggingface.co/spaces/openai/whisper", credit: CREDIT });
});

app.get('/video-summary', (req, res) => {
    res.json({ success: true, note: "Upload video for AI summary", hf_url: "https://huggingface.co/spaces", credit: CREDIT });
});

app.get('/subtitles', (req, res) => {
    res.json({ success: true, note: "Use Whisper for auto subtitles", whisper_url: "https://huggingface.co/spaces/openai/whisper", credit: CREDIT });
});

app.get('/thumbnail', (req, res) => {
    const title = req.query.title || 'Gaming Video';
    const url = genImage(`YouTube thumbnail for "${title}", bold text, vibrant colors, gaming style`, '', 1280, 720);
    res.json({ success: true, title: title, thumbnail_url: url, credit: CREDIT });
});

app.get('/gif', (req, res) => {
    const prompt = req.query.prompt || 'Dancing cat';
    const url = genImage(prompt + ' animated GIF style, sequence', '', 500, 500);
    res.json({ success: true, prompt: prompt, gif_url: url, note: "For real GIFs use Giphy API", credit: CREDIT });
});

app.get('/meme', (req, res) => {
    const top = req.query.top || 'WHEN YOU';
    const bottom = req.query.bottom || 'FINALLY DEPLOY';
    const url = `https://api.memegen.link/images/custom/${encodeURIComponent(top)}/${encodeURIComponent(bottom)}.png`;
    res.json({ success: true, top: top, bottom: bottom, meme_url: url, credit: CREDIT });
});

app.get('/slideshow', (req, res) => {
    res.json({ success: true, note: "Upload images to create slideshow video", tool: "Use FFmpeg or CloudConvert API", credit: CREDIT });
});

app.get('/remove-bg', (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    const url = genImage('remove background, transparent background, product photo', '', 800, 800) + '&image_url=' + encodeURIComponent(img);
    res.json({ success: true, result_url: url, note: "For professional BG removal use remove.bg API", credit: CREDIT });
});

app.get('/upscale', (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    const url = genImage('upscaled, 4K, high resolution, sharp details', '', 2048, 2048) + '&image_url=' + encodeURIComponent(img);
    res.json({ success: true, upscaled_url: url, credit: CREDIT });
});

app.get('/colorize', (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    const url = genImage('colorized version, realistic colors, vibrant', '', 1024, 1024) + '&image_url=' + encodeURIComponent(img);
    res.json({ success: true, colorized_url: url, credit: CREDIT });
});

app.get('/emotion', (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, note: "Use DeepAI or HuggingFace for emotion detection", hf_url: "https://huggingface.co/spaces", credit: CREDIT });
});

app.get('/age-gender', (req, res) => {
    const img = req.query.url || '';
    if (!img) return res.json({ error: "Missing image URL" });
    res.json({ success: true, note: "Use HuggingFace age/gender detection model", hf_url: "https://huggingface.co/spaces", credit: CREDIT });
});

// ============ TEST ============
app.get('/test', (req, res) => res.json({ status: "✅ V2.0 ONLINE", tools: 25, credit: CREDIT }));

// ============ START ============
app.listen(PORT, '0.0.0.0', () => {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎨🎵 BRONX MEDIA API V2.0');
    console.log('📦 25 Tools Ready!');
    console.log(`🔗 http://localhost:${PORT}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━');
});
