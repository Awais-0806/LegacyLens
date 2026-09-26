from .models import CodeMetrics
def analyze_metrics(data):
 loc=0; sizes=[]; todos=0; deep=[]
 for p in data['files']:
  try:
   text=p.read_text(encoding='utf-8',errors='ignore'); loc+=len(text.splitlines()); todos+=text.lower().count('todo')+text.lower().count('fixme'); sizes.append((data['rel'](p),p.stat().st_size))
  except OSError: pass
  if len(p.relative_to(data['root']).parts)>6: deep.append(data['rel'](p))
 return CodeMetrics(total_loc=loc,average_file_size_bytes=round(sum(s for _,s in sizes)/max(len(sizes),1),2),largest_files=[{'path':p,'size_bytes':s} for p,s in sorted(sizes,key=lambda x:-x[1])[:10]],todo_count=todos,deeply_nested_paths=deep[:20])
