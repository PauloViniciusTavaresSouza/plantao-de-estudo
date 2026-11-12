import json,re,sys,pdfplumber
pdf=pdfplumber.open(sys.argv[1]); ini,fim=int(sys.argv[2]),int(sys.argv[3])
linhas=[]
for i in range(ini-1,fim):
    p=pdf.pages[i];w=p.width
    for box in ((0,40,w/2,p.height-30),(w/2,40,w,p.height-30)):
        linhas+= (p.crop(box).extract_text() or '').splitlines()
LIXO=re.compile(r'^(Exame Nacional de Residência|INSTITUTO AOCP|ENFERMAGEM|.*Tipo 0\d – Página \d+|Página \d+)$')
linhas=[l.strip() for l in linhas if l.strip() and not LIXO.match(l.strip())]
qs=[];esp=1;atual=None
for l in linhas:
    l=re.sub(r'^\(\s*([A-E])\s*\)',r'(\1)',l)
    if l==str(esp):
        atual={'numero':esp,'enunciado':[],'alternativas':[]};qs.append(atual);esp+=1;continue
    if atual is None: continue
    m=re.match(r'^\(([A-E])\)\s*(.*)$',l)
    if m and (len(atual['alternativas'])==ord(m.group(1))-65):
        atual['alternativas'].append({'letra':m.group(1),'texto':[m.group(2)]})
    elif atual['alternativas']: atual['alternativas'][-1]['texto'].append(l)
    else: atual['enunciado'].append(l)
def junta(p):
    s=' '.join(p); s=re.sub(r'(\w)- (\w)',r'\1\2',s); return re.sub(r'\s+',' ',s).strip()
out=[];prob=[]
for q in qs:
    alts=[{'letra':a['letra'],'texto':junta(a['texto'])} for a in q['alternativas']]
    if len(alts)!=5: prob.append(q['numero'])
    out.append({'numero':q['numero'],'enunciado':junta(q['enunciado']),'alternativas':alts,'texto_apoio':None})
json.dump(out,open(sys.argv[4],'w'),ensure_ascii=False,indent=1)
print(len(out),'questões; problemas:',prob)
