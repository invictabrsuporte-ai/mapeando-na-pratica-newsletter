#!/usr/bin/env python3
"""Coleta vagas abertas de processos / melhoria contínua em portais públicos, sem login e sem chave.
Fontes (cada uma independente: se uma cair, as outras seguem): Gupy, Vagas.com e LinkedIn (busca pública).
Uso: python3 coletar_vagas.py [dias=8] [saida=vagas.json]
Regras: publicada nos últimos N dias, link respondendo, sem duplicatas, no máximo 2 por empresa,
12 vagas no máximo, fontes intercaladas. Sai com código 0 se >= 5 vagas, 2 se menos (o arquivo é gravado igual)."""
import html, json, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

DIAS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
SAIDA = sys.argv[2] if len(sys.argv) > 2 else 'vagas.json'
MAX_VAGAS, MIN_OK, MAX_POR_EMPRESA = 12, 5, 2
TERMOS = ['analista de processos', 'especialista em processos', 'coordenador de processos', 'gerente de processos',
          'melhoria contínua', 'excelência operacional', 'analista de bpm', 'gestão de processos', 'automação de processos']
RELEVANTE = re.compile(r'process|melhoria|excel[eê]ncia|bpm|lean|governan', re.I)
EXCLUIR = re.compile(r'metal|efluente|ambiental|aciaria|siderurg|qu[ií]mic|cabos|estágio|estagio|trainee|aprendiz|engenharia|engenheiro|eletr|soldag|fundi|produ[cç][aã]o|laborat|operador|manuten|seletivo|m[eé]dic|enfermeir|psic[oó]log|ginecolog|psiquiatr|jur[ií]dic|advog|dentist|farmac', re.I)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; MapeandoNaPratica-newsletter)', 'Accept-Language': 'pt-BR,pt;q=0.9'}
GENERICO = re.compile(r'^(p[áa]gina de carreira|vagas abertas|carreiras?$)', re.I)
UF = {'Acre':'AC','Alagoas':'AL','Amapá':'AP','Amazonas':'AM','Bahia':'BA','Ceará':'CE','Distrito Federal':'DF','Espírito Santo':'ES','Goiás':'GO','Maranhão':'MA','Mato Grosso':'MT','Mato Grosso do Sul':'MS','Minas Gerais':'MG','Pará':'PA','Paraíba':'PB','Paraná':'PR','Pernambuco':'PE','Piauí':'PI','Rio de Janeiro':'RJ','Rio Grande do Norte':'RN','Rio Grande do Sul':'RS','Rondônia':'RO','Roraima':'RR','Santa Catarina':'SC','São Paulo':'SP','Sergipe':'SE','Tocantins':'TO'}
MOD = {'on-site': 'Presencial', 'hybrid': 'Híbrido', 'remote': 'Remoto'}
BRT = timezone(timedelta(hours=-3))
agora = datetime.now(timezone.utc)
corte = agora - timedelta(days=DIAS)


def get(url, tentativas=2):
    for i in range(tentativas):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception as ex:
            if i == tentativas - 1:
                raise
            time.sleep(2)


def link_ok(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).status == 200
    except Exception:
        return False


def limpa(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def vaga(fonte, emp, cargo, local, pub, url):
    emp = emp.split(' | ')[0].strip()  # tira sufixos de marketing do nome da empresa
    if ' | ' in cargo:  # títulos com prefixo de marketing: fica o trecho que descreve o cargo
        cargo = next((x for x in cargo.split(' | ') if RELEVANTE.search(x)), cargo).strip()
    if len(cargo) > 95:
        cargo = cargo[:92].rstrip() + '...'
    return {'fonte': fonte, 'emp': emp, 'cargo': cargo, 'local': local, 'pub_dt': pub, 'url': url}


# ---------- fontes ----------
def fonte_gupy(termo):
    s = get('https://portal.gupy.io/job-search/term=' + urllib.parse.quote(termo))
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', s, re.S)
    out = []
    for j in json.loads(m.group(1))['props']['pageProps']['initialJobList']['data']:
        pub = datetime.fromisoformat(j['publishedDate'].replace('Z', '+00:00'))
        prazo = j.get('applicationDeadline')
        if prazo and datetime.fromisoformat(prazo.replace('Z', '+00:00')) < agora:
            continue
        emp = j['careerPageName'].strip()
        if 'confidencial' in emp.lower() or GENERICO.search(emp):
            continue
        mod = MOD.get(j.get('workplaceType'), 'Não informado')
        uf = UF.get(j.get('state', '').strip(), j.get('state', '').strip())
        local = mod if mod == 'Remoto' else f"{j.get('city', '').strip()} - {uf} · {mod}"
        out.append(vaga('Gupy', emp, j['name'].strip(), local, pub, j['jobUrl'].split('?')[0]))
    return out


def fonte_vagascom(termo):
    s = get('https://www.vagas.com.br/vagas-de-' + urllib.parse.quote(termo.replace(' ', '-')))
    out = []
    for bloco in re.split(r'<li class="vaga ', s)[1:]:
        m = re.search(r'href="(/vagas/v\d+/[^"]+)"[^>]*>(.*?)</a>', bloco, re.S)
        emp = re.search(r'class="emprVaga">(.*?)</span>', bloco, re.S)
        loc = re.search(r'bx-map"></i>\s*(.*?)\s*<div', bloco, re.S)
        dt = re.search(r'class="data-publicacao">.*?</i>\s*(.*?)\s*</span>', bloco, re.S)
        if not (m and emp and dt):
            continue
        rel = limpa(dt.group(1)).lower()
        if rel.startswith('hoje'):
            dias = 0
        elif rel.startswith('ontem'):
            dias = 1
        else:
            n = re.search(r'(\d+)\s*dia', rel)
            if not n:
                continue
            dias = int(n.group(1))
        pub = (agora - timedelta(days=dias)).replace(hour=12, minute=0, second=0, microsecond=0)
        out.append(vaga('Vagas.com', limpa(emp.group(1)), limpa(m.group(2)), limpa(loc.group(1)) if loc else 'Não informado',
                        pub, 'https://www.vagas.com.br' + m.group(1)))
    return out


def fonte_linkedin(termo):
    # busca pública de vagas (a mesma que aparece sem login); f_TPR=r604800 = última semana
    u = ('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=' + urllib.parse.quote(termo)
         + '&location=Brazil&f_TPR=r604800&start=0')
    s = get(u)
    out = []
    for bloco in s.split('<li>')[1:]:
        url = re.search(r'class="base-card__full-link[^"]*"\s+href="([^"]+)"', bloco)
        cargo = re.search(r'base-search-card__title">\s*(.*?)\s*</h3>', bloco, re.S)
        emp = re.search(r'base-search-card__subtitle">(.*?)</h4>', bloco, re.S)
        loc = re.search(r'job-search-card__location">\s*(.*?)\s*</span>', bloco, re.S)
        dt = re.search(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})"', bloco)
        if not (url and cargo and emp and dt):
            continue
        link = html.unescape(url.group(1)).split('?')[0]
        pub = datetime.fromisoformat(dt.group(1)).replace(hour=12, tzinfo=timezone.utc)
        local = limpa(loc.group(1)).replace(', Brazil', '').replace(', Brasil', '') if loc else 'Não informado'
        out.append(vaga('LinkedIn', limpa(emp.group(1)), limpa(cargo.group(1)), local, pub, link))
    return out


FONTES = [('Gupy', fonte_gupy), ('Vagas.com', fonte_vagascom), ('LinkedIn', fonte_linkedin)]

# ---------- coleta ----------
vistos, por_fonte, status = set(), {n: [] for n, _ in FONTES}, {}
for nome, fn in FONTES:
    erros = 0
    for t in TERMOS:
        try:
            achadas = fn(t)
        except Exception as ex:
            erros += 1
            print(f'[{nome}] falha no termo "{t}": {str(ex)[:80]}', file=sys.stderr)
            time.sleep(1)
            continue
        for v in achadas:
            if v['pub_dt'] < corte:
                continue
            if not RELEVANTE.search(v['cargo']) or EXCLUIR.search(v['cargo']):
                continue
            chave = (re.sub(r'\W+', '', v['emp'].lower()), re.sub(r'\W+', '', v['cargo'].lower()))
            if v['url'] in vistos or chave in vistos:
                continue
            vistos.add(v['url']); vistos.add(chave)
            por_fonte[nome].append(v)
        time.sleep(1.5)
    status[nome] = f'{len(por_fonte[nome])} candidatas, {erros}/{len(TERMOS)} termos com erro'
    por_fonte[nome].sort(key=lambda v: v['pub_dt'], reverse=True)

# ---------- seleção: intercala as fontes, valida o link, limita por empresa ----------
por_emp, saida, idx = {}, [], {n: 0 for n, _ in FONTES}
while len(saida) < MAX_VAGAS and any(idx[n] < len(por_fonte[n]) for n, _ in FONTES):
    for nome, _ in FONTES:
        if len(saida) >= MAX_VAGAS:
            break
        while idx[nome] < len(por_fonte[nome]):
            v = por_fonte[nome][idx[nome]]
            idx[nome] += 1
            emp = v['emp']
            if por_emp.get(emp.lower(), 0) >= MAX_POR_EMPRESA:
                continue
            if not link_ok(v['url']):
                continue
            por_emp[emp.lower()] = por_emp.get(emp.lower(), 0) + 1
            saida.append(v)
            break

saida.sort(key=lambda v: v['pub_dt'], reverse=True)
final = [{'emp': v['emp'], 'cargo': v['cargo'], 'local': v['local'],
          'pub': v['pub_dt'].astimezone(BRT).strftime('%d/%m/%Y'), 'url': v['url'], 'fonte': v['fonte']} for v in saida]
json.dump(final, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(final)} vagas gravadas em {SAIDA} (janela de {DIAS} dias) | ' + ' | '.join(f'{k}: {v}' for k, v in status.items()))
sys.exit(0 if len(final) >= MIN_OK else 2)
