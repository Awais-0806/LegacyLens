from pathlib import Path
from .models import LanguageSummary
MAP={'py':'Python','js':'JavaScript','jsx':'JavaScript','ts':'TypeScript','tsx':'TypeScript','java':'Java','go':'Go','rs':'Rust','c':'C','h':'C','cpp':'C++','cs':'C#','php':'PHP','rb':'Ruby','kt':'Kotlin','swift':'Swift','html':'HTML','css':'CSS','sql':'SQL','sh':'Shell'}
def detect_languages(data):
 files=data['files']; counts={}; loc={}; ev={}
 for p in files:
  lang=MAP.get(p.suffix.lower().lstrip('.')); 
  if not lang: continue
  counts[lang]=counts.get(lang,0)+1; ev.setdefault(lang,[]).append(data['rel'](p))
  try: loc[lang]=loc.get(lang,0)+sum(1 for _ in p.open('r',encoding='utf-8',errors='ignore'))
  except OSError: pass
 total=sum(counts.values()) or 1
 return [LanguageSummary(language=k,file_count=v,loc=loc.get(k,0),share=round(v/total,3),confidence='high',evidence_files=ev[k][:10]) for k,v in sorted(counts.items(),key=lambda x:-x[1])]
