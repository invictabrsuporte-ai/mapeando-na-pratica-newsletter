#!/usr/bin/env python3
"""Coleta vagas abertas de processos/melhoria contínua no portal da Gupy (dados do próprio portal, sem login).
Uso: python3 coletar_vagas.py [dias=8] [saida=vagas.json]
Regras: publicada nos últimos N dias, prazo de candidatura no futuro, link respondendo 200,
sem duplicatas, no máximo 2 por empresa, 12 vagas no máximo (10 no mínimo = sucesso; abaixo disso sai com código 2)."""
import json, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

DIAS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SAIDA = sys.argv[2] if len(sys.argv) > 2 else 'vagas.json'
TERMOS = ['analista de processos', 'especialista em processos', 'coordenador de processos', 'gerente de processos',
          'melhoria contínua', 'excelência operacional', 'analista de bpm', 'lean', 'gestão de processos', 'automação de processos']
RELEVANTE = re.compile(r'process|melhoria|excel[eê]ncia|bpm|lean|governan', re.I)
EXCLUIR = re.compile(r'metal|efluente|ambiental|aciaria|siderurg|qu[ií]mic|cabos|estágio|estagio|trainee|jovem aprendiz|engenharia|engenheiro|eletr|soldag|fundi', re.I)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; MapeandoNaPratica-newsletter)'}
GENERICO = re.compile(r'^(p[áa]gina de carreira|vagas abertas|carreiras?$)', re.I)
UF = {'Acre':'AC','Alagoas':'AL','Amapá':'AP','Amazonas':'AM','Bahia':'BA','Ceará':'CE','Distrito Federal':'DF','Espírito Santo':'ES','Goiás':'GO','Maranhão':'MA','Mato Grosso':'MT','Mato Grosso do Sul':'MS','Minas Gerais':'MG','Pará':'PA','Paraíba':'PB','Paraná':'PR','Pernambuco':'PE','Piauí':'PI','Rio de Janeiro':'RJ','Rio Grande do Norte':'RN','Rio Grande do Sul':'RS','Rondônia':'RO','Roraima':'RR','Santa Catarina':'SC','São Paulo':'SP','Sergipe':'SE','Tocantins':'TO'}
MOD = {'on-site': 'Presencial', 'hybrid': 'Híbrido', 'remote': 'Remoto'}

def pagina(termo):
    url = 'https://portal.gupy.io/job-search/term=' + urllib.parse.quote(termo)
    req = urllib.request.Request(url, headers=UA)
    s = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', s, re.S)
    return json.loads(m.group(1))['props']['pageProps']['initialJobList']['data']

def ok(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).status == 200
    except Exception:
        return False

agora = datetime.now(timezone.utc)
corte = agora - timedelta(days=DIAS)
vistos, cand = set(), []
for t in TERMOS:
    try:
        jobs = pagina(t)
    except Exception as ex:
        print('falha no termo', t, ex, file=sys.stderr); continue
    for j in jobs:
        pub = datetime.fromisoformat(j['publishedDate'].replace('Z', '+00:00'))
        prazo = j.get('applicationDeadline')
        if pub < corte: continue
        if prazo and datetime.fromisoformat(prazo.replace('Z', '+00:00')) < agora: continue
        nome, emp = j['name'].strip(), j['careerPageName'].strip()
        if not RELEVANTE.search(nome) or EXCLUIR.search(nome) or 'confidencial' in emp.lower() or GENERICO.search(emp): continue
        chave = (emp.lower(), re.sub(r'\W+', '', nome.lower()))
        if j['id'] in vistos or chave in vistos: continue
        vistos.add(j['id']); vistos.add(chave)
        cand.append((pub, j))
    time.sleep(1)

cand.sort(key=lambda x: x[0], reverse=True)
por_emp, saida = {}, []
for pub, j in cand:
    emp = j['careerPageName'].strip()
    if por_emp.get(emp, 0) >= 2: continue
    url = j['jobUrl'].split('?')[0]
    if not ok(url): continue
    por_emp[emp] = por_emp.get(emp, 0) + 1
    mod = MOD.get(j.get('workplaceType'), 'Não informado')
    uf = UF.get(j.get('state', '').strip(), j.get('state', '').strip())
    local = mod if mod == 'Remoto' else f"{j.get('city','').strip()} - {uf} · {mod}"
    saida.append({'emp': emp, 'cargo': j['name'].strip(), 'local': local,
                  'pub': pub.astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y'), 'url': url})
    if len(saida) >= 12: break

json.dump(saida, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(saida)} vagas gravadas em {SAIDA} (janela de {DIAS} dias, {len(cand)} candidatas)')
sys.exit(0 if len(saida) >= 10 else 2)
