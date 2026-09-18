#!/usr/bin/env python3
"""Build the gif-vault web gallery.

Scans projects/<project>/<set>/gifs/*.gif, extracts first-frame thumbnails,
and regenerates docs/index.html (a dependency-free viewer) plus docs/data.json.

Run from the repo root:  python3 tools/build_gallery.py
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = os.path.join(ROOT, "projects")
DOCS = os.path.join(ROOT, "docs")
THUMBS = os.path.join(DOCS, "thumbs")
THUMB_W = 256

# Public Pages URL of this repo, used for "copy direct link".
PAGES_BASE = "https://x-cessive.github.io/gif-vault/"


def scan():
    items = []
    for project in sorted(os.listdir(PROJECTS)):
        pdir = os.path.join(PROJECTS, project)
        if not os.path.isdir(pdir) or project.startswith("_"):
            continue
        for set_name in sorted(os.listdir(pdir)):
            sdir = os.path.join(pdir, set_name)
            gdir = os.path.join(sdir, "gifs")
            if not os.path.isdir(gdir):
                continue
            giphy = {}
            res_path = os.path.join(sdir, "giphy_upload_results.json")
            if os.path.exists(res_path):
                with open(res_path) as fh:
                    giphy = json.load(fh)
            for fn in sorted(os.listdir(gdir)):
                if not fn.lower().endswith(".gif"):
                    continue
                stem = fn[:-4]
                src = os.path.join(gdir, fn)
                with Image.open(src) as im:
                    w, h = im.size
                    im.seek(0)
                    thumb = im.convert("RGB")
                thumb.thumbnail((THUMB_W, THUMB_W), Image.NEAREST)
                tdir = os.path.join(THUMBS, project, set_name)
                os.makedirs(tdir, exist_ok=True)
                tpath = os.path.join(tdir, stem + ".png")
                thumb.save(tpath)
                size_kb = round(os.path.getsize(src) / 1024)
                # match a giphy result whose state key appears at the end of the stem
                giphy_url = None
                for state, r in giphy.items():
                    if isinstance(r, dict) and r.get("url") and stem.endswith(state):
                        giphy_url = r["url"]
                        break
                items.append({
                    "project": project,
                    "set": set_name,
                    "name": stem.replace("_", " "),
                    "file": fn,
                    "gif": f"../projects/{project}/{set_name}/gifs/{fn}",
                    "thumb": f"thumbs/{project}/{set_name}/{stem}.png",
                    "page_url": f"{PAGES_BASE}projects/{project}/{set_name}/gifs/{fn}",
                    "width": w,
                    "height": h,
                    "size_kb": size_kb,
                    "giphy_url": giphy_url,
                })
    return items


HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GIF Vault</title>
<style>
:root{--bg:#0b0e14;--panel:#12161f;--line:#232a3a;--txt:#dbe2ef;--dim:#8b94a7;--acc:#22d3ee}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh}
header{position:sticky;top:0;z-index:10;background:rgba(11,14,20,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:14px 20px}
.top{display:flex;align-items:center;gap:14px;flex-wrap:wrap;max-width:1200px;margin:0 auto}
h1{font-size:20px;letter-spacing:2px;font-weight:800}
h1 span{color:var(--acc)}
.count{color:var(--dim);font-size:13px}
#search{margin-left:auto;background:var(--panel);border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px 12px;font-size:14px;width:220px}
#search:focus{outline:none;border-color:var(--acc)}
.chips{display:flex;gap:8px;flex-wrap:wrap;max-width:1200px;margin:12px auto 0;padding:0 20px}
.chip{background:var(--panel);border:1px solid var(--line);color:var(--dim);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer}
.chip.on{border-color:var(--acc);color:var(--acc)}
main{max-width:1200px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;cursor:pointer;transition:transform .12s,border-color .12s}
.card:hover{transform:translateY(-2px);border-color:var(--acc)}
.card img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:#000;image-rendering:pixelated}
.meta{padding:10px 12px}
.meta .n{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta .s{font-size:12px;color:var(--dim);margin-top:4px;display:flex;gap:6px;align-items:center}
.badge{font-size:11px;background:#1a2233;border:1px solid var(--line);border-radius:6px;padding:1px 7px;color:var(--acc)}
.empty{color:var(--dim);text-align:center;padding:60px 20px;font-size:15px}
#lb{position:fixed;inset:0;background:rgba(4,6,10,.92);display:none;align-items:center;justify-content:center;z-index:50;padding:20px}
#lb.open{display:flex}
.box{background:var(--panel);border:1px solid var(--line);border-radius:16px;max-width:640px;width:100%;overflow:hidden}
.box img{width:100%;max-height:60vh;object-fit:contain;background:#000;display:block;image-rendering:auto}
.box .info{padding:16px 18px}
.box h2{font-size:18px;margin-bottom:6px}
.box .sub{color:var(--dim);font-size:13px;margin-bottom:12px}
.rows{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:13px;margin-bottom:14px}
.rows dt{color:var(--dim)} .rows dd{color:var(--txt)}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{background:#1a2233;border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;text-decoration:none}
.btn:hover{border-color:var(--acc);color:var(--acc)}
.btn.acc{background:var(--acc);border-color:var(--acc);color:#04222a;font-weight:700}
.nav{position:absolute;top:50%;transform:translateY(-50%);background:rgba(20,26,40,.85);border:1px solid var(--line);color:var(--txt);font-size:22px;width:46px;height:46px;border-radius:50%;cursor:pointer}
#prev{left:14px} #next{right:14px}
#close{position:absolute;top:14px;right:16px;background:none;border:none;color:var(--dim);font-size:26px;cursor:pointer}
#close:hover{color:var(--txt)}
footer{color:var(--dim);font-size:12px;text-align:center;padding:24px}
</style>
</head>
<body>
<header><div class="top">
<h1>GIF <span>VAULT</span></h1>
<span class="count" id="count"></span>
<input id="search" type="search" placeholder="search gifs...">
</div></header>
<div class="chips" id="chips"></div>
<main><div class="grid" id="grid"></div><div class="empty" id="empty" hidden>no gifs match</div></main>
<div id="lb"><button id="close" title="close">&times;</button>
<button class="nav" id="prev" title="previous">&#8592;</button>
<button class="nav" id="next" title="next">&#8594;</button>
<div class="box"><img id="lbimg" alt=""><div class="info">
<h2 id="lbname"></h2><div class="sub" id="lbsub"></div>
<dl class="rows"><dt>project</dt><dd id="lbproj"></dd><dt>set</dt><dd id="lbset"></dd>
<dt>size</dt><dd id="lbsize"></dd><dt>file</dt><dd id="lbfile"></dd></dl>
<div class="btns"><a class="btn acc" id="lbgiphy" target="_blank" rel="noopener" hidden>Giphy page</a>
<button class="btn" id="lbcopy">copy direct link</button>
<a class="btn" id="lbdl" download>download gif</a></div>
</div></div></div>
<footer>gif-vault &mdash; click any gif for the full view</footer>
<script>
const ITEMS = __ITEMS__;
let fProject='all', fQ='', shown=[], idx=0;
const grid=document.getElementById('grid'), empty=document.getElementById('empty'),
      count=document.getElementById('count'), chips=document.getElementById('chips'),
      search=document.getElementById('search'), lb=document.getElementById('lb');
const projects=[...new Set(ITEMS.map(i=>i.project))];
function drawChips(){chips.innerHTML='';
 [['all','all'],...projects.map(p=>[p,p])].forEach(([v,l])=>{
  const b=document.createElement('button');b.className='chip'+(fProject===v?' on':'');
  b.textContent=l==='all'?'all projects':l;b.onclick=()=>{fProject=v;draw();};chips.appendChild(b);});}
function draw(){drawChips();
 shown=ITEMS.filter(i=>(fProject==='all'||i.project===fProject)&&
  (!fQ||(i.name+' '+i.project+' '+i.set).toLowerCase().includes(fQ)));
 count.textContent=shown.length+' / '+ITEMS.length+' gifs';
 grid.innerHTML='';empty.hidden=shown.length>0;
 shown.forEach((it,k)=>{const c=document.createElement('div');c.className='card';
  c.innerHTML='<img loading="lazy" src="'+it.thumb+'" alt="">'+
   '<div class="meta"><div class="n">'+it.name+'</div>'+
   '<div class="s"><span class="badge">'+it.project+'</span><span>'+it.set+'</span></div></div>';
  c.onclick=()=>openLb(k);grid.appendChild(c);});}
function openLb(k){idx=k;const it=shown[idx];
 document.getElementById('lbimg').src=it.gif;
 document.getElementById('lbname').textContent=it.name;
 document.getElementById('lbsub').textContent=it.project+' / '+it.set;
 document.getElementById('lbproj').textContent=it.project;
 document.getElementById('lbset').textContent=it.set;
 document.getElementById('lbsize').textContent=it.width+'x'+it.height+' · '+it.size_kb+' KB';
 document.getElementById('lbfile').textContent=it.file;
 const g=document.getElementById('lbgiphy');
 if(it.giphy_url){g.hidden=false;g.href=it.giphy_url;}else g.hidden=true;
 document.getElementById('lbdl').href=it.gif;
 lb.classList.add('open');}
function closeLb(){lb.classList.remove('open');document.getElementById('lbimg').src='';}
document.getElementById('close').onclick=closeLb;
lb.addEventListener('click',e=>{if(e.target===lb)closeLb();});
document.getElementById('prev').onclick=e=>{e.stopPropagation();openLb((idx-1+shown.length)%shown.length);};
document.getElementById('next').onclick=e=>{e.stopPropagation();openLb((idx+1)%shown.length);};
document.addEventListener('keydown',e=>{if(!lb.classList.contains('open'))return;
 if(e.key==='Escape')closeLb();
 if(e.key==='ArrowLeft')openLb((idx-1+shown.length)%shown.length);
 if(e.key==='ArrowRight')openLb((idx+1)%shown.length);});
document.getElementById('lbcopy').onclick=function(){const it=shown[idx];
 const done=()=>{this.textContent='copied!';setTimeout(()=>this.textContent='copy direct link',1500);};
 if(navigator.clipboard)navigator.clipboard.writeText(it.page_url).then(done,done);
 else{const t=document.createElement('textarea');t.value=it.page_url;document.body.appendChild(t);
  t.select();try{document.execCommand('copy');}catch(e){}t.remove();done();}};
search.addEventListener('input',()=>{fQ=search.value.trim().toLowerCase();draw();});
draw();
</script>
</body>
</html>
"""


def main():
    os.makedirs(DOCS, exist_ok=True)
    items = scan()
    with open(os.path.join(DOCS, "data.json"), "w") as fh:
        json.dump(items, fh, indent=2)
    html = HTML_HEAD.replace("__ITEMS__", json.dumps(items))
    with open(os.path.join(DOCS, "index.html"), "w") as fh:
        fh.write(html)
    with open(os.path.join(DOCS, ".nojekyll"), "w") as fh:
        fh.write("")
    print(f"gallery built: {len(items)} gifs -> docs/index.html")


if __name__ == "__main__":
    main()
