```markdown
# Komponenten-Ordner (components)

Dieses Verzeichnis enthält einzelne Komponenten-Module für `status.py`. Ziel ist, den Kern-Code in `status.py` schlank zu halten und jede Komponente separat pflegbar zu machen.

Platzierung
- Lege das Verzeichnis `components/` auf derselben Ebene wie `status.py` ab.
- Erstelle eine leere Datei `components/__init__.py`, damit das Verzeichnis als Python-Package importierbar ist.

Erwartete API / Signatur
- Jede Komponente muss eine Funktion `render(...)` bereitstellen mit folgender Signatur:

```python
def render(cf, draw, device, y, font, rectangle_y, term=None) -> int:
    """
    - cf: configuration dictionary (aus config.json)
    - draw: PIL.ImageDraw drawing context
    - device: luma device object
    - y: aktuelle y-Position (int)
    - font: verwendete PIL Font
    - rectangle_y: Höhe einer Text-/Zeilenbox (int)
    - term: optionales terminal-Objekt (bei design == 'terminal')
    Returns:
    - neue y-Position (int), also y + Zeilenhöhe nach dem Rendern
    """
```

- Die Funktion sollte keine Seiteneffekte im globalen Namensraum von `status.py` erzeugen.
- Logging über das vorhandene `logging`-Modul ist empfohlen (z. B. `logging.debug(...)`).

Beispiel: Template-Komponente
```python
# components/example.py
import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    # Beispiel: einfache Textzeile
    if cf.get('design') == 'beauty':
        draw.text((0, y), 'Exmp', font=font, fill=cf['font']['color'])
        draw.text((cf['boxmarginleft'], y), 'Example component', font=font, fill=cf['font']['color'])
        y += cf['linefeed']
    elif cf.get('design') == 'terminal' and term is not None:
        term.println('Example component')
        time.sleep(2)
    logging.debug('Example component rendered')
    return y
```

Dynamisches Laden in `status.py`
- `status.py` sollte Komponenten dynamisch importieren. Beispielablauf (vereinfachter Ausschnitt):

```python
import importlib
try:
    module = importlib.import_module(f'components.{componentname}')
    y = module.render(cf, draw, device, y, font, rectangle_y, term if 'term' in locals() else None)
except ModuleNotFoundError:
    draw.text((0, y), f'{componentname} module missing', font=font, fill='RED')
    y += cf['linefeed']
    logging.error('components.%s module not found', componentname)
except Exception as e:
    draw.text((0, y), f'{componentname} error', font=font, fill='RED')
    y += cf['linefeed']
    logging.exception('Error while rendering %s component: %s', componentname, e)
```

Best Practices
- Komponenten sollten nur die Bibliotheken importieren, die sie benötigen.
- Fehler innerhalb einer Komponente dürfen nicht das ganze Programm abbrechen — fange Ausnahmen ab und logge sie.
- Halte die `render`-Funktion deterministisch: sie soll nur zeichnen und den neuen y-Wert zurückgeben.
- Falls eine Komponente auf zusätzliche Daten (z. B. `hostname`, `alert`) angewiesen ist, kannst du diese per Parameter ergänzen oder aus `cf` beziehen. Dokumentiere das dann in der Komponente.

Tests & Troubleshooting
- Test lokal: `python3 status.py` (ggf. in einer Umgebung, die luma/luma.device ersetzt oder ein Terminal-Design verwendet).
- Wenn `ModuleNotFoundError` auftritt: prüfe, dass `components/` im selben Verzeichnis wie `status.py` liegt und `__init__.py` vorhanden ist.
- Nutze `logging`-Datei/Level gemäß `config.json`, um Fehlerdetails nachzulesen.

Weiteres
- Falls du viele Komponenten hast: optional eine kleine Prüf-Routine bauen, die vor dem Hauptloop sicherstellt, dass für jede in `cf['components']` aufgeführte Komponente eine Datei unter `components/` existiert — so bekommst du frühzeitig Warnungen.

Viel Erfolg — wenn du willst, erstelle ich noch:
- ein `components/template.py`-Datei-Template in deinem Repo, oder
- eine Prüf-Utility (z. B. `components/check_components.py`) die fehlende Module meldet.
```
