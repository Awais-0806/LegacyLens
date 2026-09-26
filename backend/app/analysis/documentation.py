from .models import DocumentationSummary
def analyze_documentation(data):
 fs=[data['rel'](p) for p in data['files'] if p.name.lower().startswith(('readme','contributing','changelog')) or p.suffix.lower() in {'.md','.rst'}]
 return DocumentationSummary(files=fs,has_readme=any(p.lower().split('/')[-1].startswith('readme') for p in fs),categories={'readme':any('readme' in p.lower() for p in fs),'contributing':any('contributing' in p.lower() for p in fs),'architecture':any('architecture' in p.lower() for p in fs)})
