from pathlib import Path
import os, stat, zipfile, tarfile
from .limits import IngestionLimits
class ArchiveSecurityError(ValueError): pass
def safe_member_path(root:Path,name:str,limit:int)->Path:
 if '\x00' in name or len(name)>limit: raise ArchiveSecurityError('Unsafe archive path')
 p=Path(name)
 if p.is_absolute() or p.drive or '..' in p.parts: raise ArchiveSecurityError('Path traversal detected')
 out=(root/p).resolve()
 if out!=root and root not in out.parents: raise ArchiveSecurityError('Path escapes workspace')
 return out
def extract_archive(data:bytes, root:Path, limits:IngestionLimits):
 root.mkdir(parents=True,exist_ok=True); count=0; total=0
 import io
 try:
  z=zipfile.ZipFile(io.BytesIO(data))
  for i in z.infolist():
   count+=1
   if count>limits.max_extraction_files: raise ArchiveSecurityError('Extraction file limit exceeded')
   out=safe_member_path(root,i.filename,limits.max_path_length)
   if i.is_dir(): out.mkdir(parents=True,exist_ok=True); continue
   if i.file_size>limits.max_file_size_mb*1024**2 or total+i.file_size>limits.max_total_extracted_size_mb*1024**2: raise ArchiveSecurityError('Extraction size limit exceeded')
   out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(z.read(i)); total+=i.file_size
  return
 except zipfile.BadZipFile: pass
 try:
  t=tarfile.open(fileobj=io.BytesIO(data),mode='r:*')
  for m in t.getmembers():
   count+=1
   if count>limits.max_extraction_files or m.issym() or m.islnk(): raise ArchiveSecurityError('Unsafe archive member')
   out=safe_member_path(root,m.name,limits.max_path_length)
   if m.isdir(): out.mkdir(parents=True,exist_ok=True); continue
   if not m.isfile() or m.size>limits.max_file_size_mb*1024**2 or total+m.size>limits.max_total_extracted_size_mb*1024**2: raise ArchiveSecurityError('Extraction size limit exceeded')
   out.parent.mkdir(parents=True,exist_ok=True); src=t.extractfile(m); out.write_bytes(src.read()); total+=m.size
  return
 except tarfile.TarError as e: raise ArchiveSecurityError('Malformed or unsupported archive') from e
 raise ArchiveSecurityError('Malformed or unsupported archive')
