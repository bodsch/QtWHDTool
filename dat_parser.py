# dat_parser.py
from models import Entry

class DatParser:
    """
    Minimalparser für Retroplay-ähnliche .dat Dateien.
    Erwartet Blöcke mit Key=Value. Passt bei Bedarf an reales Format an.
    """
    def parse(self, text:str)->list[Entry]:
        items=[]
        cur={}
        for line in text.splitlines():
            line=line.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                if cur:
                    items.append(self._mk(cur)); cur={}
                continue
            if "=" in line:
                k,v=line.split("=",1); cur[k.strip().lower()]=v.strip()
        if cur: items.append(self._mk(cur))
        return items

    def _mk(self, d:dict)->Entry:
        name=d.get("name","unknown")
        version=d.get("version","")
        lang=d.get("language","")
        size=int(d.get("size","0") or 0)
        url=d.get("url","")
        crc=d.get("crc","")
        return Entry(name,version,lang,size,url,crc)
