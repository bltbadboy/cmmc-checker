from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import hashlib

app = FastAPI(title="Hello API", version="1.0.0")

class HelloResponse(BaseModel):
    message: str

class PaletteResponse(BaseModel):
    seed: str
    colors: list[str]
    keywords: list[str]

@app.get("/hello/{name}", response_model=HelloResponse)
async def hello_name(name: str):
    """
    Return a greeting message for the given name.
    """
    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    
    return HelloResponse(message=f"Hello, {name}!")

@app.get("/palette", response_model=PaletteResponse)
async def get_palette(s: str = Query(..., description="Seed keyword for palette generation")):
    """
    Generate a color palette based on a seed keyword.
    """
    if not s or s.strip() == "":
        raise HTTPException(status_code=422, detail="s must not be blank")
    
    # Seed random with the keyword for deterministic colors
    seed_hash = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
    random.seed(seed_hash)
    
    # Generate 5 deterministic hex colors
    colors = []
    for _ in range(5):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        colors.append(f"#{r:02x}{g:02x}{b:02x}")
    
    # Generate 5 related keywords
    keywords = [
        s.lower(),
        f"{s}-vibe",
        f"{s}-soft", 
        f"{s}-bold",
        f"{s}-contrast"
    ]
    
    return PaletteResponse(seed=s, colors=colors, keywords=keywords)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Color Palette Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { text-align: center; }
            input { padding: 10px; font-size: 16px; width: 200px; margin: 10px; }
            button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .palette { display: flex; justify-content: center; margin: 20px 0; }
            .color-swatch { width: 100px; height: 100px; margin: 5px; border: 1px solid #ccc; display: flex; align-items: end; justify-content: center; color: white; text-shadow: 1px 1px 1px black; cursor: pointer; position: relative; }
            .color-swatch:hover { opacity: 0.8; }
            .tooltip { position: absolute; top: -30px; left: 50%; transform: translateX(-50%); background: #333; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap; z-index: 1000; }
            .error { color: red; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Color Palette Generator</h1>
            <input type="text" id="keyword" placeholder="Enter a keyword (e.g., sunset)" />
            <button onclick="generatePalette()">Generate</button>
            <div id="error" class="error"></div>
            <div id="palette" class="palette"></div>
        </div>
        
        <script>
            window.addEventListener('load', function() {
                const saved = localStorage.getItem('paletteKeyword');
                if (saved) document.getElementById('keyword').value = saved;
            });
            
            async function generatePalette() {
                const keyword = document.getElementById('keyword').value.trim();
                const errorDiv = document.getElementById('error');
                const paletteDiv = document.getElementById('palette');
                
                if (!keyword) {
                    errorDiv.textContent = 'Please enter a keyword';
                    paletteDiv.innerHTML = '';
                    return;
                }
                
                localStorage.setItem('paletteKeyword', keyword);
                
                try {
                    const response = await fetch(`/palette?s=${encodeURIComponent(keyword)}`);
                    if (!response.ok) {
                        const error = await response.json();
                        errorDiv.textContent = error.detail || 'Error generating palette';
                        paletteDiv.innerHTML = '';
                        return;
                    }
                    
                    const data = await response.json();
                    errorDiv.textContent = '';
                    
                    paletteDiv.innerHTML = data.colors.map(color => 
                        `<div class="color-swatch" style="background-color: ${color}" onclick="copyToClipboard('${color}', this)">
                            ${color}
                        </div>`
                    ).join('');
                    
                } catch (err) {
                    errorDiv.textContent = 'Network error: ' + err.message;
                    paletteDiv.innerHTML = '';
                }
            }
            
            function copyToClipboard(text, element) {
                navigator.clipboard.writeText(text).then(() => showTooltip(element))
                .catch(() => {
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    showTooltip(element);
                });
            }
            
            function showTooltip(element) {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = 'copied!';
                element.appendChild(tooltip);
                setTimeout(() => tooltip.parentNode?.removeChild(tooltip), 1500);
            }
            
            document.getElementById('keyword').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') generatePalette();
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)