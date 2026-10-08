#!/usr/bin/env python3
"""Gera os 3 arquivos de uma edição (md, html web, html e-mail) a partir de um JSON de conteúdo.
Uso: python3 gerar_edicao.py conteudo-NN.json [vagas.json]
Saída: edicao-NN-AAAA-MM-DD.md / .html / -email.html no diretório atual."""
import json, os, sys, html, urllib.parse
if len(sys.argv) < 2: sys.exit(__doc__)
C = json.load(open(sys.argv[1], encoding='utf-8'))
VP = sys.argv[2] if len(sys.argv) > 2 else 'vagas.json'
OUT = '.'
N = C['numero']; DATE_ISO = C['data_iso']; DATE_PT = C['data_pt']
BASE = f'edicao-{N}-{DATE_ISO}'
vagas = json.load(open(VP, encoding='utf-8'))
TALLY_CASE = 'https://tally.so/r/yPLQ64'
CLAUDECODE = 'https://mapeandonapratica.com/claudecode/'
ADS = 'https://wa.me/5542991658573?text=Quero%20saber%20como%20divulgar%20minha%20empresa%20na%20newsletter.'
NAVY, ORANGE, BG, INK, MUT = '#1A2744', '#EA580C', '#F1EBDD', '#1F2937', '#5B6472'
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

def mailto(letter, text):
    subj = f'Cenario Edicao {N} - Resposta {letter}'
    body = f'Resposta do cenario - Edicao {N}: OPCAO {letter} - {text}'
    return 'mailto:invictabrsuporte@gmail.com?subject=' + urllib.parse.quote(subj) + '&body=' + urllib.parse.quote(body)

# ------------------------- Markdown -------------------------
md = []
md.append('PENDÊNCIAS PARA PUBLICAÇÃO\n\n' + '\n'.join('- ' + x for x in pend) + '\n\n---\n')
md.append('PROMPT DA IMAGEM DE CABEÇALHO\n\nCrie uma imagem horizontal, 1200x600px, para o cabeçalho de uma newsletter corporativa sobre processos e IA. Título exato em destaque: "MAPEANDO NA PRÁTICA". Subtítulo curto: "' + TAGLINE + '". Fundo bege claro (#EEE9E9), mascote simpático do projeto, tipografia forte em azul-marinho (#1A2744) com detalhe laranja (#EA580C).\n\n---\n')
md.append('## A. Metadados editoriais\n\n**Sugestões de assunto (até 55 caracteres):**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(subjects)) + f'\n\n**Assunto usado no envio:** {SUBJECT_SEND}\n\n**Preheaders (até 90 caracteres):**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(preheaders)) + f'\n\n**Slug:** {BASE}\n\n**Tempo estimado de leitura:** 7 minutos\n\n---\n')
md.append(f'# MAPEANDO NA PRÁTICA\nProcessos, melhoria contínua, automação e IA sem enrolação.\n\nEdição #{int(N)} — {DATE_PT}\n\nBom dia! Boa semana pra quem trabalha com processo.\n\n---\n')
md.append('## Antes de começar\n\n' + abertura + '\n\n---\n')
for n in news:
    md.append(f'## {n["h"]}\n\n' + '\n\n'.join(n['p']) + f'\n\nFonte: [{n["src"]}]({n["url"]}) — {n["date"]}\n\n---\n')
md.append('## ⚡ Radar rápido — Você precisa saber\n\n' + '\n\n'.join(f'→ **{a}**: {b} [Leia]({c})' for a, b, c in radar) + '\n\n---\n')
md.append(f'## 🛠️ Aplique na segunda-feira — {aplique["title"]}\n\n**Problema que resolve:** {aplique["problema"]}\n\n**Passo a passo:**\n' + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(aplique['passos'])) + f'\n\n**Ferramenta ou template necessário:** {aplique["ferramenta"]}\n\n**Duração estimada:** {aplique["duracao"]}\n\n**Resultado esperado:** {aplique["resultado"]}\n\n---\n')
md.append(f'## 🧠 Pausa para pensar — Cenário da semana\n\n**O cenário:** {pausa["cenario"]}\n\n**A pergunta:** {pausa["pergunta"]}\n\n' + '\n\n'.join(f'{l}) {t}\n[Responder {l}]({mailto(l, m)})' for l, t, m in pausa['opts']) + f'\n\n**Nosso palpite de editor:** {pausa["palpite"]}\n\n---\n')
md.append(f'## 🔧 Ferramenta da semana — {ferramenta["nome"]}\n\n**O que é:** {ferramenta["oque"]} [{ferramenta["url"]}]({ferramenta["url"]})\n\n**Problema que resolve:** {ferramenta["problema"]}\n\n**Melhor uso:** {ferramenta["uso"]}\n\n**Limitação:** {ferramenta["limitacao"]}\n\n**Exemplo prático:** {ferramenta["exemplo"]}\n\n---\n')
if vagas:
    md.append('## 💼 Oportunidades em Processos\n\nVagas publicadas entre 01 e 08/10/2026 no portal da Gupy (data de publicação conforme exibido no portal).\n\n| Cargo | Empresa | Local/Modalidade | Publicada em | Link |\n|---|---|---|---|---|\n' + '\n'.join(f'| {v["cargo"]} | {v["emp"]} | {v["local"]} | {v["pub"]} | [Ver vaga]({v["url"]}) |' for v in vagas) + '\n\nAs vagas podem ser encerradas ou alteradas pelas empresas a qualquer momento.\n\n---\n')
md.append('## 📚 Conteúdo para salvar\n\n' + '\n'.join(f'- **{t}:** [{n}]({u}) — {d}' for t, n, u, d in salvar) + '\n\n---\n')
md.append(f'## ✍️ Pergunta do leitor\n\n{pergunta}\n\nResponda este e-mail — sua resposta pode aparecer, sem identificação, na próxima edição.\n\n---\n')
md.append(f'## 📣 Publicidade\n\n**👀 Sua empresa aqui.** Alcance gestores, analistas e consultores de processos toda edição. [Quero anunciar →]({ADS})\n\n---\n')
md.append(f'## Fechamento\n\n{fechamento} [Compartilhar meu case →]({TALLY_CASE})\n\nQuero aprender Claude Code na prática? [Conhecer o curso]({CLAUDECODE}).\n\nAté a próxima edição.\n\n---\n')
md.append('CHECKLIST DO EDITOR (não publicar)\n\n- [x] Notícias principais com fonte, data e link aberto nas páginas oficiais.\n- [x] 12 vagas com link individual aberto em 08/10/2026 (ver PENDÊNCIAS sobre a Kuehne+Nagel).\n- [x] Sem vagas duplicadas.\n- [ ] Radar: itens de Lean/eventos não têm data de publicação (ver PENDÊNCIAS).\n- [x] Versão de e-mail sem <img>, sem background-image, sem <style> e sem JavaScript.\n- [ ] Link de inscrição pública da newsletter: pendente (formulário não existe).\n')
open(os.path.join(OUT, BASE + '.md'), 'w', encoding='utf-8').write('\n'.join(md))

# ------------------------- HTML helpers -------------------------
def p(text, color=INK, size=16, extra=''):
    # **negrito** simples
    parts = text.split('**')
    out = ''
    for i, t in enumerate(parts):
        t = e(t)
        out += f'<strong>{t}</strong>' if i % 2 else t
    return f'<p style="margin:0 0 14px 0; {FONT} font-size:{size}px; line-height:1.6; color:{color}; {extra}">{out}</p>'

def h2(text):
    return f'<h2 style="margin:0 0 12px 0; {SANS} font-size:22px; line-height:1.25; color:{NAVY};">{e(text)}</h2>'

def a(url, text, color=ORANGE):
    return f'<a href="{e(url, quote=True)}" style="color:{color}; text-decoration:underline; font-weight:bold;">{e(text)}</a>'

def section(inner, bg='#FFFFFF'):
    return f'<tr><td style="padding:0 0 16px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{bg}; border-radius:10px;"><tr><td style="padding:24px 28px;">{inner}</td></tr></table></td></tr>'

def btn(url, text):
    return f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 4px 0;"><tr><td style="background-color:{ORANGE}; border-radius:6px; padding:12px 22px;"><a href="{e(url, quote=True)}" style="{SANS} font-size:15px; font-weight:bold; color:#FFFFFF; text-decoration:none;">{e(text)}</a></td></tr></table>'

def build(web=False):
    rows = []
    # cabeçalho
    if web:
        rows.append('<tr><td style="padding:0 0 16px 0;"><img src="header-banner.jpg" alt="Mapeando na Prática" width="600" style="display:block; width:100%; max-width:600px; border-radius:10px;" /></td></tr>')
    else:
        rows.append(f'<tr><td style="padding:0 0 16px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{NAVY}; border-radius:10px;"><tr><td align="center" style="padding:34px 20px;"><div style="{SANS} font-size:30px; font-weight:bold; letter-spacing:1px; color:#FFFFFF;">MAPEANDO NA PRÁTICA</div><div style="{SANS} font-size:15px; color:{ORANGE}; margin-top:8px;">A dose de processos do seu dia.</div><div style="{SANS} font-size:12px; color:#CBD5E1; margin-top:14px;">Edição #{int(N)} · {DATE_PT}</div></td></tr></table></td></tr>')
    rows.append(section(p('Bom dia! Boa semana pra quem trabalha com processo.', MUT, 15) + h2('Antes de começar') + p(abertura)))
    for n in news:
        inner = h2(n['h']) + ''.join(p(t) for t in n['p']) + p(f'Fonte: {a(n["url"], n["src"])} · {e(n["date"])}'.replace('&amp;', '&'), MUT, 13).replace('&lt;', '<') if False else ''
        body = h2(n['h']) + ''.join(p(t) for t in n['p'])
        body += f'<p style="margin:0; {SANS} font-size:13px; color:{MUT};">Fonte: {a(n["url"], n["src"])} · {e(n["date"])}</p>'
        rows.append(section(body))
    rad = ''.join(f'<p style="margin:0 0 12px 0; {FONT} font-size:15px; line-height:1.55; color:{INK};">→ <strong>{e(x)}</strong>: {e(y)} {a(z, "Leia")}</p>' for x, y, z in radar)
    rows.append(section(h2('⚡ Radar rápido — Você precisa saber') + rad))
    ap = h2('🛠️ Aplique na segunda-feira — ' + aplique['title'])
    ap += p('**Problema que resolve:** ' + aplique['problema'])
    ap += p('**Passo a passo:**', INK, 16, 'margin-bottom:6px;')
    ap += ''.join(p(f'{i+1}. {s}', INK, 15, 'margin-bottom:8px;') for i, s in enumerate(aplique['passos']))
    ap += p('**Ferramenta ou template necessário:** ' + aplique['ferramenta']) + p('**Duração estimada:** ' + aplique['duracao']) + p('**Resultado esperado:** ' + aplique['resultado'])
    rows.append(section(ap, '#FFF7ED'))
    pz = h2('🧠 Pausa para pensar — Cenário da semana') + p('**O cenário:** ' + pausa['cenario']) + p('**A pergunta:** ' + pausa['pergunta'])
    for l, t, m in pausa['opts']:
        pz += p(f'**{l})** {t}', INK, 15, 'margin-bottom:4px;') + f'<p style="margin:0 0 12px 0;">{a(mailto(l, m), "Responder " + l)}</p>'
    pz += p('Clique em A, B ou C: abre um e-mail já pronto para registrarmos sua resposta. Sua resposta pode aparecer, sem identificação, na próxima edição.', MUT, 14)
    pz += p('**Nosso palpite de editor:** ' + pausa['palpite'], INK, 15)
    rows.append(section(pz))
    fe = h2('🔧 Ferramenta da semana — ' + ferramenta['nome']) + p('**O que é:** ' + ferramenta['oque'] + ' ') + f'<p style="margin:0 0 14px 0;">{a(ferramenta["url"], ferramenta["url"])}</p>' + p('**Problema que resolve:** ' + ferramenta['problema']) + p('**Melhor uso:** ' + ferramenta['uso']) + p('**Limitação:** ' + ferramenta['limitacao']) + p('**Exemplo prático:** ' + ferramenta['exemplo'])
    rows.append(section(fe))
    # vagas
    if vagas:
        th = f'style="padding:8px 6px; background-color:{NAVY}; color:#FFFFFF; text-align:left; font-size:12px;"'
        td = 'style="padding:9px 6px; border-bottom:1px solid #E5E7EB; vertical-align:top;"'
        tr = ''
        for i, v in enumerate(vagas):
            bgc = '#FFFFFF' if i % 2 == 0 else '#F8F5EE'
            tr += f'<tr style="background-color:{bgc};"><td {td}><strong>{e(v["cargo"])}</strong></td><td {td}>{e(v["emp"])}</td><td {td}>{e(v["local"])}</td><td {td}>{e(v["pub"])}</td><td {td}>{a(v["url"], "Ver vaga")}</td></tr>'
        vg = h2('💼 Oportunidades em Processos') + p('Vagas publicadas entre 01 e 08/10/2026 no portal da Gupy (data conforme exibida no portal).', MUT, 14)
        vg += f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse; {SANS} font-size:13px; line-height:1.4; color:{INK};"><tr><th {th}>Cargo</th><th {th}>Empresa</th><th {th}>Local</th><th {th}>Publicada</th><th {th}>Link</th></tr>{tr}</table>'
        vg += p('As vagas podem ser encerradas ou alteradas pelas empresas a qualquer momento.', MUT, 13, 'margin-top:12px;')
        rows.append(section(vg))
    sv = h2('📚 Conteúdo para salvar') + ''.join(f'<p style="margin:0 0 10px 0; {FONT} font-size:15px; line-height:1.55; color:{INK};"><strong>{e(t)}:</strong> {a(u, n)} — {e(d)}</p>' for t, n, u, d in salvar)
    rows.append(section(sv))
    rows.append(section(h2('✍️ Pergunta do leitor') + p(pergunta) + p('Responda este e-mail — sua resposta pode aparecer, sem identificação, na próxima edição.', MUT, 14), '#FFF7ED'))
    rows.append(f'<tr><td style="padding:0 0 16px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#E5E7EB; border-radius:10px;"><tr><td style="padding:16px 28px; {SANS} font-size:14px; color:{INK};"><strong>📣 Publicidade</strong> · <strong>👀 Sua empresa aqui.</strong> Alcance gestores, analistas e consultores de processos toda edição. {a(ADS, "Quero anunciar →")}</td></tr></table></td></tr>')
    fc = h2('Fechamento') + p(fechamento) + btn(TALLY_CASE, 'Compartilhar meu case →') + p(f'Quero aprender Claude Code na prática? {a(CLAUDECODE, "Conhecer o curso")}.'.replace('&amp;', '&'), INK, 15, 'margin-top:12px;') if False else ''
    fc = h2('Fechamento') + p(fechamento) + btn(TALLY_CASE, 'Compartilhar meu case →')
    fc += f'<p style="margin:12px 0 14px 0; {FONT} font-size:15px; color:{INK};">Quero aprender Claude Code na prática? {a(CLAUDECODE, "Conhecer o curso")}.</p>' + p('Até a próxima edição.')
    rows.append(section(fc))
    unsub = 'mailto:invictabrsuporte@gmail.com?subject=' + urllib.parse.quote('Descadastrar newsletter') + '&body=' + urllib.parse.quote('Quero deixar de receber a newsletter Mapeando na Prática.')
    rows.append(f'<tr><td align="center" style="padding:8px 20px 28px 20px; {SANS} font-size:12px; line-height:1.6; color:{MUT};">Você recebe este e-mail porque pediu a newsletter Mapeando na Prática ao preencher o formulário do bônus da aula. <a href="{unsub}" style="color:{MUT}; text-decoration:underline;">Descadastrar</a> · Invicta Consultoria · @mapeandonapratica</td></tr>')
    title = f'Mapeando na Prática NEWS — Edição #{int(N)}'
    pre = f'<div style="display:none; max-height:0; overflow:hidden; font-size:1px; color:{BG};">{e(preheaders[0])}</div>'
    return (f'<title>{title}</title>\n{pre}\n<div style="margin:0; padding:0; background-color:{BG}; width:100%;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{BG}; padding:24px 0;">\n<tr>\n<td align="center">\n'
            f'<table role="presentation" width="600" align="center" cellpadding="0" cellspacing="0" style="width:600px; max-width:600px;">\n' + '\n'.join(rows) + '\n</table>\n</td>\n</tr>\n</table>\n</div>\n')

open(os.path.join(OUT, BASE + '-email.html'), 'w', encoding='utf-8').write(build(False))
open(os.path.join(OUT, BASE + '.html'), 'w', encoding='utf-8').write(build(True))
em = open(os.path.join(OUT, BASE + '-email.html'), encoding='utf-8').read()
print('email bytes', len(em.encode('utf-8')), '| img', em.count('<img'), '| style-tag', em.count('<style'), '| bg-image', em.count('background-image'), '| script', em.count('<script'))
print('vagas', len(vagas))
