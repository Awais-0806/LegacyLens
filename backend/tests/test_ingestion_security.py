import io, zipfile
from pathlib import Path
import pytest
from app.services.url_validation import validate_public_github_url
from app.ingestion.archive import extract_archive,ArchiveSecurityError
from app.ingestion.limits import IngestionLimits
@pytest.mark.parametrize('u',[ 'http://github.com/a/b','https://evil.com/a/b','https://github.com/a/b?x=1','https://user:pass@github.com/a/b','file:///tmp/x'])
def test_bad_urls(u):
 with pytest.raises(ValueError): validate_public_github_url(u)
def test_zip_slip(tmp_path):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:z.writestr('../evil.txt','x')
 with pytest.raises(ArchiveSecurityError): extract_archive(b.getvalue(),tmp_path,IngestionLimits())
def test_absolute_path(tmp_path):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:z.writestr('/evil.txt','x')
 with pytest.raises(ArchiveSecurityError): extract_archive(b.getvalue(),tmp_path,IngestionLimits())
