"""Versão WEB editorial da newsletter (GitHub Pages). Usada por gerar_edicao.py.
Não é usada no e-mail: o e-mail continua em tabelas, sem <style>/<img>/<script> (Gmail remove).
Imagens: ilustrações geradas com PIL (sem texto repetido do título) em img/ed-*.webp."""
import os, re, html, math, urllib.parse
e = html.escape
NAVY, ORANGE, BG = '#1A2744', '#EA580C', '#EEE9E9'
TAGCOL = {'IA': '#7C3AED', 'BPM': '#EA580C', 'LEAN': '#0F766E', 'PROCESSOS': '#EA580C', 'AUTOMAÇÃO': '#2563EB', 'BPMN': '#EA580C'}


def limpo(t):
    """remove emojis/pictogramas dos títulos na versão web"""
    return re.sub(r'[\u2190-\u2BFF\u2600-\u27BF\U0001F000-\U0001FAFF\uFE0F]', lambda m: '→' if m.group() == '→' else '', t).strip()


def rich(t):
    out = ''
    for i, part in enumerate(t.split('**')):
        out += f'<strong>{e(part)}</strong>' if i % 2 else e(part)
    return out


# ---------------------------------------------------------------- ilustrações
def ilustracoes(news, N):
    """Gera ilustrações editoriais 1600x900 por matéria. Retorna {indice: (arquivo, alt)}"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return {}
    os.makedirs('img', exist_ok=True)
    S = 2  # supersampling
    W, H = 1600 * S, 900 * S

    def font(sz, bold=True):
        for p in ('C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
            if os.path.exists(p):
                return ImageFont.truetype(p, int(sz * 1.55 * S))
        return ImageFont.load_default()

    def hexa(h):
        h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    PAPER, INKL, MUTE = hexa('#F6F1EA'), hexa('#1A2744'), hexa('#6B7280')

    def base(accent):
        im = Image.new('RGB', (W, H), PAPER)
        d = ImageDraw.Draw(im)
        # grade pontilhada discreta
        for x in range(60 * S, W, 60 * S):
            for y in range(60 * S, H, 60 * S):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=hexa('#D9D1C6'))
        d.rectangle([0, 0, 18 * S, H], fill=accent)
        return im, d

    def box(d, x, y, w, h, label, fill=None, outline=INKL, txt=INKL, sz=24, dash=False):
        d.rounded_rectangle([x, y, x + w, y + h], 22 * S, fill=fill or PAPER)
        d.rounded_rectangle([x, y, x + w, y + h], 22 * S, outline=outline, width=4 * S)
        f = font(sz); lines = label.split('\n'); lh = sz * 1.55 * 1.25 * S
        ty = y + h / 2 - lh * len(lines) / 2
        for ln in lines:
            tw = d.textlength(ln, font=f); d.text((x + w / 2 - tw / 2, ty), ln, font=f, fill=txt); ty += lh

    def arrow(d, x1, y1, x2, y2, col=INKL, w=4):
        d.line([x1, y1, x2, y2], fill=col, width=w * S)
        ang = math.atan2(y2 - y1, x2 - x1); L = 22 * S
        for s in (-0.45, 0.45):
            d.line([x2, y2, x2 - L * math.cos(ang + s), y2 - L * math.sin(ang + s)], fill=col, width=w * S)

    def tag(d, label, accent):
        f = font(18); tw = d.textlength(label, font=f)
        d.rounded_rectangle([90 * S, 60 * S, 90 * S + tw + 48 * S, 132 * S], 36 * S, fill=accent)
        d.text((114 * S, 76 * S), label, font=f, fill=(255, 255, 255))

    def lanes(accent, tg):
        im, d = base(accent); tag(d, tg, accent)
        # raia 1: volume e regra
        d.text((90 * S, 180 * S), 'VOLUME E REGRA', font=font(20), fill=accent)
        for i in range(9):
            x = (120 + i * 60) * S; d.ellipse([x, 260 * S, x + 30 * S, 290 * S], fill=accent)
        arrow(d, 680 * S, 275 * S, 820 * S, 275 * S)
        box(d, 830 * S, 205 * S, 480 * S, 140 * S, 'modelo pequeno', fill=accent, outline=accent, txt=(255, 255, 255))
        arrow(d, 1320 * S, 275 * S, 1400 * S, 275 * S)
        d.ellipse([1410 * S, 255 * S, 1450 * S, 295 * S], fill=INKL)
        d.line([90 * S, 450 * S, 1510 * S, 450 * S], fill=hexa('#C9C0B3'), width=3 * S)
        # raia 2: exceção e julgamento
        d.text((90 * S, 480 * S), 'EXCEÇÃO E JULGAMENTO', font=font(20), fill=INKL)
        for i in range(3):
            x = (120 + i * 90) * S; d.ellipse([x, 590 * S, x + 38 * S, 628 * S], outline=INKL, width=5 * S)
        arrow(d, 440 * S, 609 * S, 820 * S, 609 * S)
        box(d, 870 * S, 540 * S, 400 * S, 140 * S, 'especialista\n+ revisão humana')
        arrow(d, 1320 * S, 609 * S, 1400 * S, 609 * S)
        d.ellipse([1410 * S, 589 * S, 1450 * S, 629 * S], fill=INKL)
        d.text((90 * S, 790 * S), 'Cada tarefa no recurso certo.', font=font(26), fill=MUTE)
        return im

    def ciclo(accent, tg):
        im, d = base(accent); tag(d, tg, accent)
        cx, cy, R = 800 * S, 520 * S, 270 * S
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=hexa('#C9C0B3'), width=4 * S)
        pts = [('ENTENDER', -90), ('AUTOMATIZAR', 30), ('MELHORAR', 150)]
        for i, (lab, deg) in enumerate(pts):
            a = math.radians(deg); x, y = cx + R * math.cos(a), cy + R * math.sin(a)
            fill = accent if i == 0 else None
            box(d, x - 190 * S, y - 58 * S, 380 * S, 116 * S, lab, fill=fill, outline=accent if i == 0 else INKL, txt=(255, 255, 255) if i == 0 else INKL, sz=26)
        # setas curtas sobre o círculo
        for deg in (-30, 90, 210):
            a = math.radians(deg); a2 = math.radians(deg + 14)
            arrow(d, cx + R * math.cos(a), cy + R * math.sin(a), cx + R * math.cos(a2), cy + R * math.sin(a2), accent, 6)
        return im

    def camadas(accent, tg):
        im, d = base(accent); tag(d, tg, accent)
        x, w = 250 * S, 1100 * S
        d.rounded_rectangle([x, 180 * S, x + w, 180 * S + 130 * S], 22 * S, outline=accent, width=4 * S)
        f = font(22); t = 'o que vem agora: pessoas, agentes e automações'; d.text((x + w / 2 - d.textlength(t, font=f) / 2, 232 * S), t, font=f, fill=accent)
        for i, lab in enumerate(['aplicações', 'dados', 'automações e processos']):
            y = (350 + i * 150) * S
            box(d, x, y, w, 120 * S, lab, fill=INKL if i == 2 else None, txt=(255, 255, 255) if i == 2 else INKL, sz=28)
        arrow(d, 800 * S, 340 * S, 800 * S, 316 * S, accent, 6)
        d.text((90 * S, 820 * S), 'Construa sobre o que já existe.', font=font(22), fill=MUTE)
        return im

    def fluxo(accent, tg):
        im, d = base(accent); tag(d, tg, accent)
        y = 450 * S; x = 150 * S
        d.ellipse([x, y - 30 * S, x + 60 * S, y + 30 * S], outline=INKL, width=6 * S); x += 60 * S
        for kind in ('t', 'g', 't', 'e'):
            arrow(d, x, y, x + 70 * S, y); x += 70 * S
            if kind == 't': d.rounded_rectangle([x, y - 55 * S, x + 200 * S, y + 55 * S], 20 * S, outline=INKL, width=5 * S); x += 200 * S
            elif kind == 'g': d.polygon([(x, y), (x + 60 * S, y - 60 * S), (x + 120 * S, y), (x + 60 * S, y + 60 * S)], outline=accent, fill=PAPER); d.line([x, y, x + 60 * S, y - 60 * S, x + 120 * S, y, x + 60 * S, y + 60 * S, x, y], fill=accent, width=6 * S); x += 120 * S
            else: d.ellipse([x, y - 30 * S, x + 60 * S, y + 30 * S], fill=accent)
        return im

    kinds = {'lanes': lanes, 'ciclo': ciclo, 'camadas': camadas}
    out = {}
    for i, n in enumerate(news):
        accent = hexa(TAGCOL.get(n['tag'].upper(), ORANGE))
        fn = kinds.get(n.get('ilustracao'), fluxo)
        im = fn(accent, n['tag'].upper()).resize((1600, 900), Image.LANCZOS)
        name = f'img/ed-{N}-{i + 1}.webp'
        im.save(name, 'WEBP', quality=84, method=6)
        im.save(name.replace('.webp', '.png'), 'PNG', optimize=True)  # para e-mail (Brevo)
        out[i] = (name, n.get('alt_imagem') or f'Ilustração: {limpo(n.get("capa") or n["h"])}')
    return out


# ---------------------------------------------------------------- página
CSS = """
:root{--bg:#EEE9E9;--paper:#FBF9F6;--navy:#1A2744;--navy2:#2A3A63;--orange:#C2410C;--orange-b:#EA580C;--ink:#1F2937;--mut:#5B6472;--line:#D8D1C7;--col:720px;--wide:980px}
*{box-sizing:border-box}html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.7 Georgia,'Iowan Old Style','Times New Roman',serif;overflow-wrap:anywhere}
a{color:var(--orange);text-underline-offset:3px;text-decoration-thickness:1px}a:hover{color:var(--navy)}
:focus-visible{outline:3px solid var(--orange-b);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-999px}.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;z-index:9}
.sans,.eyebrow,nav,.meta,.btn,figcaption,.src,.chip{font-family:'Sora',system-ui,-apple-system,'Segoe UI',Arial,sans-serif}
.top{background:var(--navy);color:#fff}.top .in{max-width:var(--wide);margin:0 auto;padding:12px 20px;display:flex;justify-content:space-between;gap:12px;align-items:center;font:600 12px/1.4 'Sora',system-ui,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase}
.top a{color:#fff;text-decoration:none}.top a:hover{color:#FDBA74}
.masthead{max-width:var(--wide);margin:28px auto 0;padding:0 20px}.masthead img{display:block;width:100%;height:auto;border-radius:18px}
.wrap{max-width:var(--col);margin:0 auto;padding:0 20px}.wide{max-width:var(--wide);margin:0 auto;padding:0 20px}
.meta{margin:44px 0 18px;font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--mut)}
.meta b{color:var(--orange)}
h1{font:800 clamp(2rem,5.2vw,3.1rem)/1.12 'Sora',system-ui,Arial,sans-serif;letter-spacing:-.02em;color:var(--navy);margin:0 0 18px;text-wrap:balance}
.sub{font-size:clamp(1.1rem,2.4vw,1.3rem);line-height:1.55;color:var(--mut);margin:0 0 26px;text-wrap:pretty}
.tools{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 36px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:12px 22px;border-radius:10px;font-size:15px;font-weight:700;text-decoration:none;border:2px solid var(--navy);color:var(--navy);background:transparent;cursor:pointer;transition:background .2s,color .2s,transform .2s}
.btn:hover{background:var(--navy);color:#fff}.btn.pri{background:var(--orange);border-color:var(--orange);color:#fff}.btn.pri:hover{background:var(--navy);border-color:var(--navy)}
.hello{font-weight:700;margin:0 0 14px}.lede{margin:0 0 40px}
figure{margin:0}figure img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:16px;background:#e4ddd3}
figcaption{font-size:12px;color:var(--mut);margin-top:8px;letter-spacing:.02em}
.toc{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px 26px;margin:0 0 56px}
.toc h2{font:700 12px/1 'Sora',system-ui,Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--orange);margin:0 0 12px}
.toc ol{margin:0;padding:0;list-style:none;counter-reset:t}.toc li{counter-increment:t;border-top:1px solid var(--line)}.toc li:first-child{border-top:0}
.toc a{display:flex;gap:14px;padding:10px 0;color:var(--navy);text-decoration:none;font:600 15px/1.4 'Sora',system-ui,Arial,sans-serif}
.toc a::before{content:counter(t,decimal-leading-zero);color:var(--orange);min-width:2ch}.toc a:hover{color:var(--orange)}
.toc small{display:block;font:400 14px/1.4 Georgia,serif;color:var(--mut)}
section.s{padding:56px 0 0;scroll-margin-top:16px}section.s+section.s{border-top:0}
.sep{max-width:var(--col);margin:56px auto 0;border:0;border-top:1px solid var(--line)}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;margin:0 0 10px}
h2.t{font:800 clamp(1.6rem,3.8vw,2.2rem)/1.2 'Sora',system-ui,Arial,sans-serif;letter-spacing:-.015em;color:var(--navy);margin:0 0 16px;text-wrap:balance}
h2.t.sm{font-size:clamp(1.35rem,3vw,1.7rem)}
.tldr{font-size:1.1rem;color:var(--mut);border-left:4px solid var(--orange-b);padding-left:16px;margin:0 0 24px}
.story p{margin:0 0 1.15em}.story figure{margin:0 0 26px}
.callout{background:var(--paper);border:1px solid var(--line);border-left:5px solid var(--orange-b);border-radius:12px;padding:18px 22px;margin:26px 0}
.callout .eyebrow{color:var(--orange);margin:0 0 6px}.callout p{margin:0;font-size:17px}
.src{font-size:13px;color:var(--mut);margin-top:22px}.src a{font-weight:700}
.rad{list-style:none;padding:0;margin:0}.rad li{padding:16px 0;border-top:1px solid var(--line);display:grid;grid-template-columns:auto 1fr;gap:6px 16px}.rad li:last-child{border-bottom:1px solid var(--line)}
.chip{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--navy);background:#E3DCD3;border-radius:999px;padding:4px 10px;align-self:start;white-space:nowrap}
.rad p{margin:0;font-size:17px;line-height:1.55}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:34px clamp(20px,5vw,40px)}
.steps{margin:0 0 20px;padding:0;list-style:none;counter-reset:s}.steps li{counter-increment:s;display:grid;grid-template-columns:2.4rem 1fr;gap:10px;margin:0 0 14px;font-size:17px;line-height:1.6}
.steps li::before{content:counter(s);font:800 15px/2rem 'Sora',sans-serif;width:2rem;height:2rem;border-radius:50%;background:var(--navy);color:#fff;text-align:center}
dl.facts{margin:0}dl.facts dt{font:700 12px/1.4 'Sora',system-ui,Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--orange);margin:18px 0 2px}dl.facts dd{margin:0;font-size:17px;line-height:1.6}
.opts{list-style:none;margin:20px 0;padding:0;display:grid;gap:12px}.opts li{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px}.opts p{margin:0 0 10px;font-size:17px;line-height:1.55}.opts .btn{min-height:42px;padding:8px 18px;font-size:14px}
.note{font-size:15px;color:var(--mut)}
.ad{background:var(--navy);color:#E2E8F0;border-radius:22px;overflow:hidden}.ad .bd{padding:clamp(24px,5vw,44px)}
.ad .eyebrow{color:#FDBA74}.ad h2{font:800 clamp(1.6rem,4vw,2.2rem)/1.15 'Sora',system-ui,Arial,sans-serif;color:#fff;margin:0 0 14px}.ad p{margin:0 0 22px;font-size:18px}
.ad .btn{background:var(--orange-b);border-color:var(--orange-b);color:#fff}.ad .btn:hover{background:#fff;color:var(--navy);border-color:#fff}
.free{list-style:none;margin:0;padding:0}.free li{padding:22px 0;border-top:1px solid var(--line)}.free li:last-child{border-bottom:1px solid var(--line)}
.free h3{font:700 1.15rem/1.3 'Sora',system-ui,Arial,sans-serif;color:var(--navy);margin:6px 0 6px}.free p{margin:0 0 8px;font-size:17px;line-height:1.55}.free a{font-family:'Sora',system-ui,Arial,sans-serif;font-weight:700;font-size:15px}
.jobs{list-style:none;margin:0;padding:0}.jobs li{padding:16px 0;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr auto;gap:4px 18px;align-items:center}.jobs li:last-child{border-bottom:1px solid var(--line)}
.jobs strong{font:700 1rem/1.35 'Sora',system-ui,Arial,sans-serif;color:var(--navy);display:block}.jobs span{font-size:15px;color:var(--mut)}.jobs a{font:700 14px 'Sora',system-ui,Arial,sans-serif;white-space:nowrap}
.save{list-style:none;margin:0;padding:0}.save li{padding:14px 0;border-top:1px solid var(--line);font-size:17px;line-height:1.55}.save li:last-child{border-bottom:1px solid var(--line)}.save b{font:700 12px 'Sora',sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--orange);display:block;margin-bottom:2px}
.close{text-align:left}.sig{display:flex;gap:16px;align-items:center;margin:28px 0 0}.sig img{width:64px;height:64px;border-radius:50%;object-fit:cover}.sig p{margin:0;line-height:1.4;font-size:16px}.sig b{font-family:'Sora',system-ui,Arial,sans-serif}
footer{margin-top:72px;background:var(--navy);color:#CBD5E1;padding:44px 0 56px;font:15px/1.7 'Sora',system-ui,Arial,sans-serif}
footer a{color:#fff}footer .links{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 22px}footer .links a{border:1px solid #475569;border-radius:10px;padding:10px 16px;text-decoration:none;font-weight:600;min-height:44px;display:inline-flex;align-items:center}footer .links a:hover{background:#fff;color:var(--navy)}
footer p{margin:0 0 12px;font-size:14px}
@media (max-width:640px){body{font-size:17.5px}.jobs li{grid-template-columns:1fr}.rad li{grid-template-columns:1fr}.toc{padding:18px}.top .in span:last-child{display:none}.tools .btn{flex:1 1 100%}}
@media (prefers-reduced-motion:no-preference){.rv{animation:rv .6s ease both}@keyframes rv{from{opacity:.001;transform:translateY(10px)}to{opacity:1;transform:none}}}
@media print{.top,.tools,.toc,footer .links{display:none}body{background:#fff}}
"""

JS = """
(function(){var b=document.getElementById('copiar');if(!b)return;b.hidden=false;var l=b.textContent;
b.addEventListener('click',function(){var u=location.href.split('#')[0];
function ok(){b.textContent='Link copiado';setTimeout(function(){b.textContent=l},2200)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(ok,function(){window.prompt('Copie o link:',u)})}
else{window.prompt('Copie o link:',u)}})})();
"""

CALLOUT_RE = re.compile(r'^\*\*(Por que importa[^*]*|Por que importa|Leitura crítica|Para aplicar)[:\*]*\s*\*?\*?:?\s*(.*)$', re.S)


def build_web(ctx):
    """ctx: dict com N, DATE_PT, DATE_ISO, BASE, WEB_URL, news, radar, abertura, aplique, pausa, ferramenta, salvar,
    pergunta, fechamento, vagas, AD, GRATUITOS, SUGESTAO, ANUNCIE, SITE, LINKEDIN, INSTAGRAM, CLAUDECODE, mailto, C"""
    g = ctx; N = g['N']; news = g['news']
    figs = ilustracoes(news, N)
    # tempo de leitura calculado pelo conteúdo
    words = len(re.sub(r'<[^>]+>', ' ', g.get('texto_total', '')).split())
    texto = [g['abertura']] + [' '.join(n['p']) + ' ' + n.get('tldr', '') for n in news]
    texto += [' '.join(t for t in g['aplique']['passos']), g['aplique']['problema'], g['pausa']['cenario'], g['ferramenta']['oque'], g['pergunta'], g['fechamento']]
    texto += [f'{a} {b}' for a, b, _ in g['radar']] + [f'{d}' for _, _, _, d in g['salvar']] + [x['desc'] for x in g['GRATUITOS']]
    words = len(' '.join(texto).split())
    mins = max(3, round(words / 200))
    titulo = g['C'].get('titulo') or g['C'].get('tagline_header', '').rstrip('.') or limpo(news[0]['h'])
    subtitulo = g['C'].get('subtitulo') or ('Nesta edição: ' + '; '.join(n.get('curto') or limpo(n['h']) for n in news) + '.')
    ids = []

    def fig(i, caption=None):
        if i not in figs: return ''
        f, alt = figs[i]
        cap = f'<figcaption>{e(caption)}</figcaption>' if caption else ''
        eager = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        return f'<figure><img src="{f}" alt="{e(alt)}" width="1600" height="900" decoding="async"{eager}>{cap}</figure>'

    def story(n, i):
        sid = f'materia-{i + 1}'; ids.append((sid, n['tag'].upper(), n.get('curto') or limpo(n['h'])))
        col = TAGCOL.get(n['tag'].upper(), ORANGE)
        body = ''
        for t in n['p']:
            m = CALLOUT_RE.match(t)
            if m and len(t) < 700:
                lab = re.sub(r'[\*:]+$', '', m.group(1)).strip()
                rest = m.group(2).strip()
                body += f'<aside class="callout"><p class="eyebrow">{e(lab)}</p><p>{rich(rest)}</p></aside>'
            else:
                body += f'<p>{rich(t)}</p>'
        tl = f'<p class="tldr">{e(n["tldr"])}</p>' if n.get('tldr') else ''
        wide = '<div class="wide">' + fig(i) + '</div>' if i == 0 else ''
        inner_fig = '' if i == 0 else fig(i)
        return (f'<section class="s story" id="{sid}"><div class="wrap">'
                f'<p class="eyebrow" style="color:{col}">{e(n["tag"])} · matéria {i + 1}</p><h2 class="t{"" if i == 0 else " sm"}">{e(limpo(n["h"]))}</h2>{tl}</div>'
                f'{wide}<div class="wrap" style="padding-top:{"28px" if i == 0 else "0"}">{inner_fig}{body}'
                f'<p class="src">Fonte: <a href="{e(n["url"], quote=True)}">{e(n["src"])}</a> · {e(n["date"])}</p></div></section>')

    parts = []
    # --- abertura
    parts.append(f'<header><div class="top"><div class="in"><a href="{g["SITE"]}">mapeandonapratica.com</a><span>Edição #{int(N)} · {e(g["DATE_PT"])}</span></div></div>'
                 f'<div class="masthead"><a href="{g["SITE"]}"><img src="header-banner.jpg" alt="Mapeando na Prática: a dose de processos do seu dia" width="1200" height="400"></a></div>'
                 f'<div class="wrap rv"><p class="meta"><b>Edição #{int(N)}</b> · {e(g["DATE_PT"])} · {mins} min de leitura</p>'
                 f'<h1>{e(titulo)}</h1><p class="sub">{e(subtitulo)}</p>'
                 f'<div class="tools"><button class="btn" id="copiar" type="button" hidden>Copiar link da edição</button><a class="btn" href="#materia-1">Começar a leitura</a></div></div></header>')
    parts.append('<main id="conteudo">')
    parts.append(f'<div class="wrap"><p class="hello">Bom dia! Boa semana pra quem trabalha com processo.</p><p class="lede">{rich(g["abertura"])}</p>')
    # sumário (preenchido depois)
    parts.append('@@TOC@@</div>')
    for i, n in enumerate(news): parts.append(story(n, i))
    # --- radar
    ids.append(('radar', 'RADAR', 'o que você precisa saber'))
    rad = ''.join(f'<li><span class="chip">{e(x)}</span><p>{e(y)} <a href="{e(z, quote=True)}">Leia</a></p></li>' for x, y, z in g['radar'])
    parts.append(f'<hr class="sep"><section class="s" id="radar"><div class="wrap"><p class="eyebrow" style="color:var(--orange)">Radar</p><h2 class="t sm">Você precisa saber</h2><ul class="rad">{rad}</ul></div></section>')
    # --- aplique
    ap = g['aplique']; ids.append(('aplique', 'NA PRÁTICA', limpo(ap['title'])))
    steps = ''.join(f'<li><span>{e(re.sub(r"^\d+[.)]\s*", "", s))}</span></li>' for s in ap['passos'])
    parts.append(f'<section class="s" id="aplique"><div class="wrap"><div class="panel"><p class="eyebrow" style="color:var(--orange)">Aplique na segunda-feira · Na prática</p><h2 class="t sm">{e(limpo(ap["title"]))}</h2>'
                 f'<p><strong>Problema que resolve:</strong> {e(ap["problema"])}</p><p><strong>Passo a passo</strong></p><ol class="steps">{steps}</ol>'
                 f'<dl class="facts"><dt>Ferramenta ou template</dt><dd>{e(ap["ferramenta"])}</dd><dt>Duração estimada</dt><dd>{e(ap["duracao"])}</dd><dt>Resultado esperado</dt><dd>{e(ap["resultado"])}</dd></dl></div></div></section>')
    # --- pausa
    pz = g['pausa']; ids.append(('pausa', 'PAUSA', 'cenário da semana'))
    opts = ''.join(f'<li><p><strong>{e(l)})</strong> {e(t)}</p><a class="btn" href="{e(g["mailto"](l, m), quote=True)}">Responder {e(l)}</a></li>' for l, t, m in pz['opts'])
    parts.append(f'<section class="s" id="pausa"><div class="wrap"><p class="eyebrow" style="color:#7C3AED">Pausa para pensar</p><h2 class="t sm">Cenário da semana</h2>'
                 f'<p><strong>O cenário:</strong> {e(pz["cenario"])}</p><p><strong>A pergunta:</strong> {e(pz["pergunta"])}</p><ul class="opts">{opts}</ul>'
                 f'<p class="note">Clique em A, B ou C: abre um e-mail já pronto para registrarmos sua resposta. Sua resposta pode aparecer, sem identificação, na próxima edição.</p>'
                 f'<aside class="callout"><p class="eyebrow">Nosso palpite de editor</p><p>{e(pz["palpite"])}</p></aside></div></section>')
    # --- ferramenta
    fe = g['ferramenta']; ids.append(('ferramenta', 'FERRAMENTA', limpo(fe['nome'])))
    parts.append(f'<section class="s" id="ferramenta"><div class="wrap"><p class="eyebrow" style="color:#2563EB">Ferramenta da semana</p><h2 class="t sm">{e(limpo(fe["nome"]))}</h2>'
                 f'<p>{rich("**O que é:** " + fe["oque"])}</p><p><a class="btn" href="{e(fe["url"], quote=True)}">Abrir a ferramenta</a></p>'
                 f'<dl class="facts"><dt>Problema que resolve</dt><dd>{e(fe["problema"])}</dd><dt>Melhor uso</dt><dd>{e(fe["uso"])}</dd><dt>Limitação</dt><dd>{e(fe["limitacao"])}</dd><dt>Exemplo prático</dt><dd>{e(fe["exemplo"])}</dd></dl></div></section>'.replace('</div></section>', '</div></section>', 1))
    # --- publi
    AD = g['AD']
    parts.append(f'<section class="s"><div class="wide"><div class="ad"><div class="bd"><p class="eyebrow">Publicidade · Curso Mapeando na Prática</p><h2>{e(AD["titulo"])}</h2><p>{e(AD["texto"])}</p>'
                 f'<a class="btn" href="{e(AD["url"], quote=True)}">{e(AD["cta"])} →</a></div></div></div></section>')
    # --- gratuitos
    ids.append(('gratuitos', 'GRÁTIS', 'cursos gratuitos para estudar'))
    fr = ''.join(f'<li><span class="chip">{e(x["tag"])}</span><h3>{e(x["nome"])}</h3><p>{e(x["desc"])}</p><a href="{e(x["url"], quote=True)}">{e(x["cta"])} →</a></li>' for x in g['GRATUITOS'])
    parts.append(f'<section class="s" id="gratuitos"><div class="wrap"><p class="eyebrow" style="color:#2563EB">Aprenda sem pagar</p><h2 class="t sm">Cursos gratuitos para a sua semana</h2>'
                 f'<p>Quatro portas de entrada para estudar sem gastar: uma de IA, uma de BPMN, uma de gestão de processos e uma de automação.</p><ul class="free">{fr}</ul>'
                 f'<p class="note" style="margin-top:14px">Gratuidade e condições são definidas por cada instituição e podem mudar.</p></div></section>')
    # --- vagas
    if g['vagas']:
        ids.append(('vagas', 'CARREIRA', f'{len(g["vagas"])} vagas em processos'))
        jb = ''.join(f'<li><div><strong>{e(v["cargo"])}</strong><span>{e(v["emp"])} · {e(v["local"])} · publicada em {e(v["pub"])}</span></div><a href="{e(v["url"], quote=True)}" aria-label="Ver vaga: {e(v["cargo"])}, {e(v["emp"])}">Ver vaga →</a></li>' for v in g['vagas'])
        parts.append(f'<section class="s" id="vagas"><div class="wrap"><p class="eyebrow" style="color:#0F766E">Carreira</p><h2 class="t sm">Oportunidades em Processos</h2>'
                     f'<p class="note">Vagas publicadas nos últimos dias no portal da Gupy (data conforme exibida no portal).</p><ul class="jobs">{jb}</ul>'
                     f'<p class="note" style="margin-top:14px">As vagas podem ser encerradas ou alteradas pelas empresas a qualquer momento.</p></div></section>')
    # --- salvar
    ids.append(('salvar', 'GUARDAR', 'conteúdo para salvar'))
    sv = ''.join(f'<li><b>{e(t)}</b><a href="{e(u, quote=True)}">{e(n)}</a> — {e(d)}</li>' for t, n, u, d in g['salvar'])
    parts.append(f'<section class="s" id="salvar"><div class="wrap"><p class="eyebrow" style="color:var(--orange)">Para guardar</p><h2 class="t sm">Conteúdo para salvar</h2><ul class="save">{sv}</ul></div></section>')
    # --- encerramento
    parts.append(f'<section class="s close" id="fim"><div class="wrap"><p class="eyebrow" style="color:var(--orange)">Sua vez</p><h2 class="t sm">Pergunta do leitor</h2><p>{e(g["pergunta"])}</p>'
                 f'<p class="note">Responda este e-mail — sua resposta pode aparecer, sem identificação, na próxima edição.</p>'
                 f'<hr class="sep" style="margin:36px 0"><h2 class="t sm">Até a próxima</h2><p>{e(g["fechamento"])}</p>'
                 f'<p><a class="btn pri" href="{e(g["SUGESTAO"], quote=True)}">O que você gostaria de ver aqui? →</a></p>'
                 f'<p>Quero aprender Claude Code na prática? <a href="{g["CLAUDECODE"]}">Conhecer o curso</a>.</p>'
                 f'<div class="sig"><img src="avatar-alan.jpg" alt="Alan Almeida" width="64" height="64" loading="lazy"><p><b>Alan Almeida</b><br><span class="note">Invicta · Mapeando na Prática</span></p></div></div></section>')
    parts.append('</main>')
    parts.append(f'<footer><div class="wrap"><div class="links"><a href="{g["SITE"]}">Invicta</a><a href="{g["LINKEDIN"]}">LinkedIn</a><a href="{g["INSTAGRAM"]}">Instagram</a></div>'
                 f'<p>Quer fazer sua marca conversar com gestores, analistas e consultores de processos? <a href="{g["ANUNCIE"]}">Anuncie</a>.</p>'
                 f'<p>Você recebe a newsletter Mapeando na Prática porque pediu ao preencher o formulário do bônus da aula. Invicta Consultoria · @mapeandonapratica</p></div></footer>')
    toc = '<nav class="toc" aria-label="Nesta edição"><h2>Nesta edição</h2><ol>' + ''.join(f'<li><a href="#{i}">{e(t)} <small>{e(d)}</small></a></li>' for i, t, d in ids) + '</ol></nav>'
    page = '\n'.join(parts).replace('@@TOC@@', toc)
    desc = g['preheaders'][0]
    return (f'<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(titulo)} · Mapeando na Prática #{int(N)}</title><meta name="description" content="{e(desc, quote=True)}">'
            f'<meta property="og:title" content="{e(titulo, quote=True)}"><meta property="og:description" content="{e(desc, quote=True)}"><meta property="og:type" content="article">'
            + (f'<meta property="og:image" content="{g["WEB_URL"].rsplit("/", 1)[0]}/{figs[0][0]}">' if 0 in figs else '') +
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap">'
            f'<style>{CSS}</style></head><body><a class="skip" href="#conteudo">Pular para o conteúdo</a>\n{page}\n<script>{JS}</script></body></html>\n')
