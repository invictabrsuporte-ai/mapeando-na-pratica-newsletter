#!/usr/bin/env python3
"""Gera os 3 arquivos de uma edição (md, html web com imagens, html de e-mail sem imagens) a partir de um JSON de conteúdo.
Uso: python3 gerar_edicao.py conteudo-NN.json [vagas.json]
Saída (no diretório atual): edicao-NN-AAAA-MM-DD.md / .html / -email.html e, para a versão web, capas em img/.
Observação: o conector de Gmail remove <img> e background-image, por isso o e-mail usa só blocos de cor, texto e emoji."""
import json, os, sys, html, urllib.parse
if len(sys.argv) < 2: sys.exit(__doc__)
C = json.load(open(sys.argv[1], encoding='utf-8'))
VP = sys.argv[2] if len(sys.argv) > 2 else 'vagas.json'
N = C['numero']; DATE_ISO = C['data_iso']; DATE_PT = C['data_pt']
BASE = f'edicao-{N}-{DATE_ISO}'
vagas = json.load(open(VP, encoding='utf-8')) if os.path.exists(VP) else []
PAGES = 'https://invictabrsuporte-ai.github.io/mapeando-na-pratica-newsletter/'
WEB_URL = PAGES + BASE + '.html'
ANUNCIE = 'https://tally.so/r/2EMMOp'
SITE = 'https://mapeandonapratica.com/invicta/'
LINKEDIN = 'https://www.linkedin.com/newsletters/mapeando-na-pr%C3%A1tica-7259255564608684033/'
INSTAGRAM = 'https://www.instagram.com/mapeandonapratica/'
CLAUDECODE = 'https://mapeandonapratica.com/claudecode/'
SUGESTAO = 'mailto:invictabrsuporte@gmail.com?subject=' + urllib.parse.quote('O que eu gostaria de ver na newsletter') + '&body=' + urllib.parse.quote('Eu gostaria de ver na newsletter: ')
AD = dict(tag='PUBLI', titulo='Domine a modelagem de processos com BPMN',
          texto='Aprenda a estruturar operações claras, padronizadas e eficientes, sem depender de sistema e sem teoria solta. Do processo confuso ao fluxo que gera controle e melhoria contínua.',
          cta='Quero dominar BPMN na prática', url='https://mapeandonapratica.com/modelagemdeprocessos/')
GRATUITOS = C.get('gratuitos') or [
    dict(tag='IA', nome='Anthropic Academy', desc='Cursos gratuitos e com certificado sobre Claude, Claude Code e agentes, com cadastro só por e-mail. Comece por "Claude 101" ou "Claude Code 101".', url='https://anthropic.skilljar.com/', cta='Ver cursos'),
    dict(tag='BPMN', nome='Camunda Academy', desc='Treinamento gratuito sob demanda em BPMN e DMN, com módulos como "BPMN Participants", "BPMN Events" e "BPMN Task Types".', url='https://academy.camunda.com/', cta='Ver cursos'),
    dict(tag='PROCESSOS', nome='Escola Virtual.Gov (Enap)', desc='Centenas de cursos gratuitos com certificado, incluindo trilhas de gestão de processos. Busque por "gestão de processos".', url='https://www.escolavirtual.gov.br/', cta='Ver cursos'),
    dict(tag='AUTOMAÇÃO', nome='Microsoft Learn', desc='Trilhas gratuitas de Power Platform, Power Automate e IA para quem quer automatizar rotinas de escritório.', url='https://learn.microsoft.com/pt-br/training/', cta='Ver trilhas'),
]
NAVY, ORANGE, BG, INK, MUT, LINE = '#1A2744', '#EA580C', '#F1EBDD', '#1F2937', '#5B6472', '#E5E7EB'
TAGCOL = {'IA': '#7C3AED', 'BPM': '#EA580C', 'LEAN': '#0F766E', 'PROCESSOS': '#EA580C', 'AUTOMAÇÃO': '#2563EB', 'BPMN': '#EA580C', 'APPS': '#2563EB', 'MODELOS': '#7C3AED', 'AGENTES': '#7C3AED', 'MERCADO': '#0F766E'}
FONT = "font-family:Georgia,'Times New Roman',serif;"
SANS = "font-family:Arial,Helvetica,sans-serif;"
e = html.escape
subjects, preheaders, SUBJECT_SEND = C['subjects'], C['preheaders'], C['SUBJECT_SEND']
abertura, news, radar = C['abertura'], C['news'], [tuple(x) for x in C['radar']]
aplique, pausa, ferramenta = C['aplique'], C['pausa'], C['ferramenta']
pausa['opts'] = [tuple(x) for x in pausa['opts']]
salvar = [tuple(x) for x in C['salvar']]
pergunta, fechamento, pend = C['pergunta'], C['fechamento'], C['pend']
TAGLINE = C.get('tagline_header', 'Cada tarefa no recurso certo.')
TAGS = ['IA', 'PROCESSOS', 'AUTOMAÇÃO']

def mailto(letter, text):
    subj = f'Cenario Edicao {N} - Resposta {letter}'
    body = f'Resposta do cenario - Edicao {N}: OPCAO {letter} - {text}'
    return 'mailto:invictabrsuporte@gmail.com?subject=' + urllib.parse.quote(subj) + '&body=' + urllib.parse.quote(body)

for i, n in enumerate(news):
    n.setdefault('tag', TAGS[i % 3])

# ---------------------- capas (só versão web) ----------------------
def capas():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return {}
    os.makedirs('img', exist_ok=True)
    def font(sz, bold=True):
        for p in ('C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
            if os.path.exists(p): return ImageFont.truetype(p, sz)
        return ImageFont.load_default()
    def wrap(d, text, f, w):
        out, line = [], ''
        for wd in text.split():
            t = (line + ' ' + wd).strip()
            if d.textlength(t, font=f) <= w: line = t
            else: out.append(line); line = wd
        out.append(line); return out
    def flow(d, x0, y, accent):
        # fluxo BPMN estilizado: início, tarefas, decisão, fim
        d.ellipse([x0, y - 22, x0 + 44, y + 22], outline='#FFFFFF', width=5)
        x = x0 + 44
        for i, kind in enumerate(['task', 'gw', 'task', 'end']):
            d.line([x, y, x + 46, y], fill=accent, width=5); x += 46
            if kind == 'task': d.rounded_rectangle([x, y - 30, x + 110, y + 30], 12, outline='#FFFFFF', width=5); x += 110
            elif kind == 'gw': d.polygon([(x, y), (x + 36, y - 36), (x + 72, y), (x + 36, y + 36)], outline=accent); d.line([x, y, x + 36, y - 36, x + 72, y, x + 36, y + 36, x, y], fill=accent, width=5); x += 72
            else: d.ellipse([x, y - 22, x + 44, y + 22], fill=accent)
    made = {}
    def make(name, tag, title, accent):
        im = Image.new('RGB', (1200, 520), NAVY)
        d = ImageDraw.Draw(im)
        for k in range(520):  # degradê vertical
            c = tuple(int(a + (b - a) * k / 520) for a, b in zip((26, 39, 68), (15, 23, 42)))
            d.line([0, k, 1200, k], fill=c)
        d.rectangle([0, 0, 14, 520], fill=accent)
        d.rounded_rectangle([60, 56, 60 + d.textlength(tag, font=font(26)) + 44, 106], 25, fill=accent)
        d.text((82, 66), tag, font=font(26), fill='#FFFFFF')
        f = font(60); y = 150
        for ln in wrap(d, title, f, 1000)[:3]:
            d.text((60, y), ln, font=f, fill='#FFFFFF'); y += 76
        flow(d, 60, 440, accent)
        d.text((880, 470), 'MAPEANDO NA PRÁTICA', font=font(24), fill='#CBD5E1')
        im.save(f'img/{name}.png', optimize=True); made[name] = f'img/{name}.png'
    for i, n in enumerate(news):
        limpo = ''.join(ch for ch in (n.get('capa') or n['h']) if ord(ch) < 0x2000 or ch in '–—·').strip()
        make(f'capa-{N}-{i+1}', n['tag'], limpo, TAGCOL.get(n['tag'].upper(), ORANGE))
    make('banner-modelagem', 'PUBLI · CURSO', 'Domine a modelagem de processos com BPMN', ORANGE)
    make('banner-gratuitos', 'CURSOS GRATUITOS', 'Aprenda sem pagar: 4 trilhas para sua semana', '#2563EB')
    return made
IMGS = capas() if '--sem-imagens' not in sys.argv else {}

# ---------------------- Markdown ----------------------
md = []
md.append('PENDÊNCIAS PARA PUBLICAÇÃO\n\n' + '\n'.join('- ' + x for x in pend) + '\n\n---\n')
md.append(f'PROMPT DA IMAGEM DE CABEÇALHO\n\nCrie uma imagem horizontal, 1200x600px, para o cabeçalho de uma newsletter corporativa sobre processos e IA. Título exato em destaque: "MAPEANDO NA PRÁTICA". Subtítulo curto: "{TAGLINE}". Fundo bege claro (#EEE9E9), mascote simpático do projeto, tipografia forte em azul-marinho (#1A2744) com detalhe laranja (#EA580C).\n\n---\n')
md.append('## A. Metadados editoriais\n\n**Sugestões de assunto (até 55 caracteres):**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(subjects)) + f'\n\n**Assunto usado no envio:** {SUBJECT_SEND}\n\n**Preheaders (até 90 caracteres):**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(preheaders)) + f'\n\n**Slug:** {BASE}\n\n**Tempo estimado de leitura:** 7 minutos\n\n---\n')
md.append(f'# MAPEANDO NA PRÁTICA\nProcessos, melhoria contínua, automação e IA sem enrolação.\n\nEdição #{int(N)} — {DATE_PT}\n\nBom dia! Boa semana pra quem trabalha com processo.\n\n---\n')
md.append('## Antes de começar\n\n' + abertura + '\n\n---\n')
for n in news:
    md.append(f'## {n["tag"]} · {n["h"]}\n\n' + ('**TL;DR:** ' + n['tldr'] + '\n\n' if n.get('tldr') else '') + '\n\n'.join(n['p']) + f'\n\nFonte: [{n["src"]}]({n["url"]}) — {n["date"]}\n\n---\n')
md.append('## ⚡ Radar rápido — Você precisa saber\n\n' + '\n\n'.join(f'→ **{a}**: {b} [Leia]({c})' for a, b, c in radar) + '\n\n---\n')
md.append(f'## 🛠️ Aplique na segunda-feira — {aplique["title"]}\n\n**Problema que resolve:** {aplique["problema"]}\n\n**Passo a passo:**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(aplique['passos'])) + f'\n\n**Ferramenta ou template necessário:** {aplique["ferramenta"]}\n\n**Duração estimada:** {aplique["duracao"]}\n\n**Resultado esperado:** {aplique["resultado"]}\n\n---\n')
md.append(f'## 🧠 Pausa para pensar — Cenário da semana\n\n**O cenário:** {pausa["cenario"]}\n\n**A pergunta:** {pausa["pergunta"]}\n\n' + '\n\n'.join(f'{l}) {t}\n[Responder {l}]({mailto(l, m)})' for l, t, m in pausa['opts']) + f'\n\n**Nosso palpite de editor:** {pausa["palpite"]}\n\n---\n')
md.append(f'## 🔧 Ferramenta da semana — {ferramenta["nome"]}\n\n**O que é:** {ferramenta["oque"]} [{ferramenta["url"]}]({ferramenta["url"]})\n\n**Problema que resolve:** {ferramenta["problema"]}\n\n**Melhor uso:** {ferramenta["uso"]}\n\n**Limitação:** {ferramenta["limitacao"]}\n\n**Exemplo prático:** {ferramenta["exemplo"]}\n\n---\n')
md.append(f'## 📣 {AD["tag"]} — {AD["titulo"]}\n\n{AD["texto"]}\n\n[{AD["cta"]} →]({AD["url"]})\n\n---\n')
md.append('## 🎓 Cursos gratuitos para a sua semana\n\n' + '\n\n'.join(f'**{g["nome"]}** ({g["tag"]}): {g["desc"]} [{g["cta"]}]({g["url"]})' for g in GRATUITOS) + '\n\n---\n')
if vagas:
    md.append('## 💼 Oportunidades em Processos\n\nVagas publicadas nos últimos dias no portal da Gupy (data de publicação conforme exibido no portal).\n\n| Cargo | Empresa | Local/Modalidade | Publicada em | Link |\n|---|---|---|---|---|\n' + '\n'.join(f'| {v["cargo"]} | {v["emp"]} | {v["local"]} | {v["pub"]} | [Ver vaga]({v["url"]}) |' for v in vagas) + '\n\nAs vagas podem ser encerradas ou alteradas pelas empresas a qualquer momento.\n\n---\n')
md.append('## 📚 Conteúdo para salvar\n\n' + '\n'.join(f'- **{t}:** [{n}]({u}) — {d}' for t, n, u, d in salvar) + '\n\n---\n')
md.append(f'## ✍️ Pergunta do leitor\n\n{pergunta}\n\nResponda este e-mail — sua resposta pode aparecer, sem identificação, na próxima edição.\n\n---\n')
md.append(f'## Fechamento\n\n{fechamento} [O que você gostaria de ver aqui? →]({SUGESTAO})\n\nQuero aprender Claude Code na prática? [Conhecer o curso]({CLAUDECODE}).\n\nAté a próxima edição.\n\n---\n')
md.append(f'Quer fazer sua marca conversar com gestores, analistas e consultores de processos? [Anuncie]({ANUNCIE}).\n\nSite: {SITE} · LinkedIn: {LINKEDIN} · Instagram: {INSTAGRAM}\n\n---\n')
md.append('CHECKLIST DO EDITOR (não publicar)\n\n- [ ] Notícias com fonte, data e link aberto nas páginas oficiais.\n- [ ] Vagas com link individual e dentro da janela.\n- [ ] Versão de e-mail sem <img>, sem background-image, sem <style> e sem JavaScript.\n')
open(BASE + '.md', 'w', encoding='utf-8').write('\n'.join(md))

# ---------------------- HTML helpers ----------------------
def p(text, color=INK, size=16, extra=''):
    parts = text.split('**'); out = ''
    for i, t in enumerate(parts):
        t = e(t); out += f'<strong>{t}</strong>' if i % 2 else t
    return f'<p style="margin:0 0 14px 0; {FONT} font-size:{size}px; line-height:1.6; color:{color}; {extra}">{out}</p>'
def tag(t, col=None):
    col = col or TAGCOL.get(t.upper(), ORANGE)
    return f'<p style="margin:0 0 6px 0; {SANS} font-size:12px; font-weight:bold; letter-spacing:1.5px; color:{col};">{e(t.upper())}</p>'
def h2(text, size=22): return f'<h2 style="margin:0 0 12px 0; {SANS} font-size:{size}px; line-height:1.25; color:{NAVY};">{e(text)}</h2>'
def a(url, text, color=ORANGE): return f'<a href="{e(url, quote=True)}" style="color:{color}; text-decoration:underline; font-weight:bold;">{e(text)}</a>'
def section(inner, bg='#FFFFFF', pad='24px 28px'):
    return f'<tr><td style="padding:0 0 16px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{bg}; border-radius:12px;"><tr><td style="padding:{pad};">{inner}</td></tr></table></td></tr>'
def btn(url, text, bg=ORANGE, col='#FFFFFF'):
    return f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 4px 0;"><tr><td style="background-color:{bg}; border-radius:8px; padding:13px 24px;"><a href="{e(url, quote=True)}" style="{SANS} font-size:15px; font-weight:bold; color:{col}; text-decoration:none;">{e(text)}</a></td></tr></table>'
def cover(name, web, alt):
    if web and name in IMGS: return f'<img src="{IMGS[name]}" alt="{e(alt)}" width="544" style="display:block; width:100%; max-width:544px; border-radius:10px; margin:0 0 16px 0;" />'
    return ''

def build(web=False):
    rows = []
    # barra superior
    rows.append(f'<tr><td align="right" style="padding:0 4px 10px 0; {SANS} font-size:12px; color:{MUT};">{e(DATE_PT)} &nbsp;|&nbsp; <a href="{WEB_URL}" style="color:{INK}; font-weight:bold;">Leia online</a></td></tr>')
    if web:
        rows.append('<tr><td style="padding:0 0 16px 0;"><img src="header-banner.jpg" alt="Mapeando na Prática" width="600" style="display:block; width:100%; max-width:600px; border-radius:12px;" /></td></tr>')
    else:
        rows.append(f'<tr><td style="padding:0 0 16px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{NAVY}; border-radius:12px;"><tr><td align="center" style="padding:34px 20px 8px 20px;"><div style="{SANS} font-size:30px; font-weight:bold; letter-spacing:1px; color:#FFFFFF;">MAPEANDO NA PRÁTICA</div><div style="{SANS} font-size:15px; color:{ORANGE}; margin-top:8px;">A dose de processos do seu dia.</div></td></tr><tr><td align="center" style="padding:6px 20px 28px 20px;"><div style="{SANS} font-size:12px; letter-spacing:2px; color:#CBD5E1; margin-top:12px;">EDIÇÃO #{int(N)} · {e(DATE_ISO[8:])}/{e(DATE_ISO[5:7])}/{e(DATE_ISO[:4])} · <a href="{SITE}" style="color:#CBD5E1; text-decoration:none;">MAPEANDONAPRATICA.COM</a></div></td></tr></table></td></tr>')
    # saudação + sumário
    sumario = ''.join(f'<p style="margin:0 0 4px 0; {FONT} font-size:15px; line-height:1.5; color:{INK};">• <strong>{e(n["tag"].upper())}</strong>: {e(n.get("curto") or n["h"])}</p>' for n in news)
    extras = [f'• <strong>Publi e cursos gratuitos</strong>: modelagem de processos com BPMN e 4 trilhas gratuitas']
    if vagas: extras.append(f'• <strong>Vagas</strong>: {len(vagas)} oportunidades abertas em processos e melhoria contínua')
    sumario += ''.join(f'<p style="margin:0 0 4px 0; {FONT} font-size:15px; line-height:1.5; color:{INK};">{x}</p>' for x in extras)
    rows.append(section(p('Bom dia! Boa semana pra quem trabalha com processo.', INK, 16, 'font-weight:bold;') + p('Na edição de hoje:', MUT, 14, 'margin-bottom:6px;') + sumario))
    rows.append(section(tag('Antes de começar', ORANGE) + p(abertura)))
    for i, n in enumerate(news):
        body = tag(n['tag']) + h2(n['h'], 24)
        if n.get('tldr'): body += p('TL;DR: ' + n['tldr'], MUT, 15)
        body += cover(f'capa-{N}-{i+1}', web, n['h']) + ''.join(p(t) for t in n['p'])
        body += f'<p style="margin:0; {SANS} font-size:13px; color:{MUT};">Fonte: {a(n["url"], n["src"])} · {e(n["date"])}</p>'
        rows.append(section(body))
    rad = ''.join(f'<p style="margin:0 0 12px 0; {FONT} font-size:15px; line-height:1.55; color:{INK};">→ <strong>{e(x)}</strong>: {e(y)} {a(z, "Leia")}</p>' for x, y, z in radar)
    rows.append(section(tag('Radar', ORANGE) + h2('⚡ Você precisa saber') + rad))
    ap = tag('Aplique na segunda-feira', ORANGE) + h2('🛠️ ' + aplique['title']) + p('**Problema que resolve:** ' + aplique['problema']) + p('**Passo a passo:**', INK, 16, 'margin-bottom:6px;')
    ap += ''.join(p(f'{i+1}. {s}', INK, 15, 'margin-bottom:8px;') for i, s in enumerate(aplique['passos']))
    ap += p('**Ferramenta ou template necessário:** ' + aplique['ferramenta'], INK, 16, 'margin-top:8px;') + p('**Duração estimada:** ' + aplique['duracao']) + p('**Resultado esperado:** ' + aplique['resultado'])
    rows.append(section(ap, '#FFF7ED'))
    pz = tag('Pausa para pensar', '#7C3AED') + h2('🧠 Cenário da semana') + p('**O cenário:** ' + pausa['cenario']) + p('**A pergunta:** ' + pausa['pergunta'])
    for l, t, m in pausa['opts']:
        pz += p(f'**{l})** {t}', INK, 15, 'margin-bottom:4px;') + f'<p style="margin:0 0 12px 0;">{a(mailto(l, m), "Responder " + l)}</p>'
    pz += p('Clique em A, B ou C: abre um e-mail já pronto para registrarmos sua resposta. Sua resposta pode aparecer, sem identificação, na próxima edição.', MUT, 14) + p('**Nosso palpite de editor:** ' + pausa['palpite'], INK, 15)
    rows.append(section(pz))
    fe = tag('Ferramenta da semana', '#2563EB') + h2('🔧 ' + ferramenta['nome']) + p('**O que é:** ' + ferramenta['oque']) + f'<p style="margin:0 0 14px 0;">{a(ferramenta["url"], ferramenta["url"])}</p>' + p('**Problema que resolve:** ' + ferramenta['problema']) + p('**Melhor uso:** ' + ferramenta['uso']) + p('**Limitação:** ' + ferramenta['limitacao']) + p('**Exemplo prático:** ' + ferramenta['exemplo'])
    rows.append(section(fe))
    # PUBLI do curso
    ad_img = f'<img src="{IMGS["banner-modelagem"]}" alt="{e(AD["titulo"])}" width="544" style="display:block; width:100%; max-width:544px; border-radius:10px; margin:0 0 16px 0;" />' if web and 'banner-modelagem' in IMGS else ''
    ad = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{NAVY}; border-radius:12px;"><tr><td style="padding:6px 0 0 0; border-top:6px solid {ORANGE}; border-radius:12px;">'
          f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="padding:22px 28px 26px 28px;">'
          f'<p style="margin:0 0 10px 0; {SANS} font-size:11px; letter-spacing:2px; color:#CBD5E1;">PUBLICIDADE · CURSO MAPEANDO NA PRÁTICA</p>'
          f'{ad_img}<h2 style="margin:0 0 10px 0; {SANS} font-size:26px; line-height:1.2; color:#FFFFFF;">{e(AD["titulo"])}</h2>'
          f'<p style="margin:0 0 16px 0; {FONT} font-size:16px; line-height:1.6; color:#E2E8F0;">{e(AD["texto"])}</p>'
          f'{btn(AD["url"], AD["cta"] + " →")}</td></tr></table></td></tr></table>')
    rows.append(f'<tr><td style="padding:0 0 16px 0;">{ad}</td></tr>')
    # cursos gratuitos
    gb = tag('Aprenda sem pagar', '#2563EB') + h2('🎓 Cursos gratuitos para a sua semana') + p('Quatro portas de entrada para estudar sem gastar: uma de IA, uma de BPMN, uma de gestão de processos e uma de automação.', MUT, 15)
    if web and 'banner-gratuitos' in IMGS: gb = f'<img src="{IMGS["banner-gratuitos"]}" alt="Cursos gratuitos" width="544" style="display:block; width:100%; max-width:544px; border-radius:10px; margin:0 0 16px 0;" />' + gb
    cards = ''
    for g in GRATUITOS:
        cards += (f'<tr><td style="padding:0 0 12px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F8F5EE; border-radius:10px;"><tr><td style="padding:16px 18px; border-left:5px solid {TAGCOL.get(g["tag"].upper(), ORANGE)}; border-radius:10px;">'
                  f'{tag(g["tag"])}<p style="margin:0 0 6px 0; {SANS} font-size:17px; font-weight:bold; color:{NAVY};">{e(g["nome"])}</p>'
                  f'<p style="margin:0 0 10px 0; {FONT} font-size:15px; line-height:1.55; color:{INK};">{e(g["desc"])}</p>{a(g["url"], g["cta"] + " →")}</td></tr></table></td></tr>')
    gb += f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{cards}</table>'
    gb += p('Gratuidade e condições são definidas por cada instituição e podem mudar.', MUT, 13)
    rows.append(section(gb))
    if vagas:
        th = f'style="padding:8px 6px; background-color:{NAVY}; color:#FFFFFF; text-align:left; font-size:12px;"'
        td = f'style="padding:9px 6px; border-bottom:1px solid {LINE}; vertical-align:top;"'
        tr = ''
        for i, v in enumerate(vagas):
            tr += f'<tr style="background-color:{"#FFFFFF" if i % 2 == 0 else "#F8F5EE"};"><td {td}><strong>{e(v["cargo"])}</strong></td><td {td}>{e(v["emp"])}</td><td {td}>{e(v["local"])}</td><td {td}>{e(v["pub"])}</td><td {td}>{a(v["url"], "Ver vaga")}</td></tr>'
        vg = tag('Carreira', '#0F766E') + h2('💼 Oportunidades em Processos') + p('Vagas publicadas nos últimos dias no portal da Gupy (data conforme exibida no portal).', MUT, 14)
        vg += f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse; {SANS} font-size:13px; line-height:1.4; color:{INK};"><tr><th {th}>Cargo</th><th {th}>Empresa</th><th {th}>Local</th><th {th}>Publicada</th><th {th}>Link</th></tr>{tr}</table>'
        vg += p('As vagas podem ser encerradas ou alteradas pelas empresas a qualquer momento.', MUT, 13, 'margin-top:12px;')
        rows.append(section(vg))
    sv = tag('Para guardar', ORANGE) + h2('📚 Conteúdo para salvar') + ''.join(f'<p style="margin:0 0 10px 0; {FONT} font-size:15px; line-height:1.55; color:{INK};"><strong>{e(t)}:</strong> {a(u, n)} — {e(d)}</p>' for t, n, u, d in salvar)
    rows.append(section(sv))
    rows.append(section(tag('Sua vez', ORANGE) + h2('✍️ Pergunta do leitor') + p(pergunta) + p('Responda este e-mail — sua resposta pode aparecer, sem identificação, na próxima edição.', MUT, 14), '#FFF7ED'))
    fc = h2('Até a próxima') + p(fechamento) + btn(SUGESTAO, 'O que você gostaria de ver aqui? →')
    fc += f'<p style="margin:14px 0 14px 0; {FONT} font-size:15px; color:{INK};">Quero aprender Claude Code na prática? {a(CLAUDECODE, "Conhecer o curso")}.</p>'
    rows.append(section(fc))
    # rodapé
    def badge(url, txt, bg):
        return f'<td style="padding:0 6px 0 0;"><a href="{url}" style="display:inline-block; background-color:{bg}; color:#FFFFFF; {SANS} font-size:13px; font-weight:bold; text-decoration:none; padding:9px 14px; border-radius:8px;">{txt}</a></td>'
    icones = f'<table role="presentation" cellpadding="0" cellspacing="0" align="center"><tr>{badge(SITE, "🌐 Invicta", NAVY)}{badge(LINKEDIN, "in LinkedIn", "#0A66C2")}{badge(INSTAGRAM, "◎ Instagram", "#C13584")}</tr></table>'
    unsub = 'mailto:invictabrsuporte@gmail.com?subject=' + urllib.parse.quote('Descadastrar newsletter') + '&body=' + urllib.parse.quote('Quero deixar de receber a newsletter Mapeando na Prática.')
    rows.append(f'<tr><td align="center" style="padding:8px 20px 8px 20px; {SANS} font-size:13px; line-height:1.6; color:{MUT};">{icones}</td></tr>')
    rows.append(f'<tr><td align="center" style="padding:14px 20px 4px 20px; {SANS} font-size:14px; line-height:1.6; color:{INK};">Quer fazer sua marca conversar com gestores, analistas e consultores de processos? <a href="{ANUNCIE}" style="color:{ORANGE}; font-weight:bold; text-decoration:underline;">Anuncie</a>.</td></tr>')
    rows.append(f'<tr><td align="center" style="padding:10px 20px 28px 20px; {SANS} font-size:12px; line-height:1.6; color:{MUT};">Você recebe este e-mail porque pediu a newsletter Mapeando na Prática ao preencher o formulário do bônus da aula. <a href="{unsub}" style="color:{MUT}; text-decoration:underline;">Descadastrar</a> · Invicta Consultoria · @mapeandonapratica</td></tr>')
    title = f'Mapeando na Prática NEWS — Edição #{int(N)}'
    pre = f'<div style="display:none; max-height:0; overflow:hidden; font-size:1px; color:{BG};">{e(preheaders[0])}</div>'
    return (f'<title>{title}</title>\n{pre}\n<div style="margin:0; padding:0; background-color:{BG}; width:100%;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{BG}; padding:24px 0;">\n<tr>\n<td align="center">\n'
            f'<table role="presentation" width="600" align="center" cellpadding="0" cellspacing="0" style="width:600px; max-width:600px;">\n' + '\n'.join(rows) + '\n</table>\n</td>\n</tr>\n</table>\n</div>\n')

open(BASE + '-email.html', 'w', encoding='utf-8').write(build(False))
open(BASE + '.html', 'w', encoding='utf-8').write(build(True))
em = open(BASE + '-email.html', encoding='utf-8').read()
print('email bytes', len(em.encode('utf-8')), '| img', em.count('<img'), '| style-tag', em.count('<style'), '| bg-image', em.count('background-image'), '| script', em.count('<script'), '| vagas', len(vagas), '| capas', len(IMGS))

# deixa as capas (img/) e os demais arquivos prontos para o commit da rotina
import subprocess
try:
    subprocess.run(['git', 'add', '-A'], check=False, capture_output=True)
except Exception:
    pass
