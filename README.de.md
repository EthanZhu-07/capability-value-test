# Capability Value Test｜Wertprüfung einer neuen Fähigkeit

[English](README.md)｜[简体中文](README.zh-CN.md)｜[繁體中文](README.zh-TW.md)｜[日本語](README.ja.md)｜[한국어](README.ko.md)｜[Русский](README.ru.md)｜[हिन्दी](README.hi.md)｜[Español](README.es.md)｜[Français](README.fr.md)｜**Deutsch**｜[Português](README.pt.md)｜[العربية](README.ar.md)

> Die Nutzung einer neuen Fähigkeit sichtbar und ihren Wert messbar machen.

Capability Value Test ist ein allgemeiner Skill für KI-Agenten. Er prüft, ob eine neu integrierte Fähigkeit (etwa Skill, Modell, Plugin, MCP Server, Browser, Open-Source-Komponente oder Agent-Workflow) tatsächlich aufgerufen wurde und gegenüber der bisherigen Methode messbaren Wert schafft.

Er entwirft einen fairen A/B-Test zwischen der bisherigen Methode und der Methode nach Integration der neuen Fähigkeit. Vor der Ausführung prüft ein Mensch den vollständigen Versuchsplan. Danach entsteht ein eigenständiger, visueller und nachvollziehbarer HTML-Bericht.

## Diese Fragen beantwortet der Skill

1. **Wurde die Fähigkeit wirklich verwendet und wo ist der Nachweis?**
2. **Hat sie Wert geschaffen und lässt sich dieser quantifizieren?**
3. **Lassen sich Nutzungsprozess und konkreter Wert visuell verstehen?**

## Ablauf

1. Neue Fähigkeit sowie die Methoden vor und nach der Integration festlegen.
2. Eine reale Aufgabe wählen, die beide Methoden erledigen können.
3. Eingaben, Umgebung, Einschränkungen, Messumfang und Bewertungskriterien angleichen.
4. Den vollständigen Plan zur menschlichen Prüfung vorlegen und bei Ablehnung überarbeiten.
5. Erst nach ausdrücklicher Freigabe beide Methoden ausführen und Ergebnisse, Metriken und Nachweise erfassen.
6. Unterschiede analysieren und den HTML-Bericht erzeugen.

Ziel ist nicht, die neue Fähigkeit gewinnen zu lassen, sondern festzustellen, was sich verändert und ob die Belege eine Einführung rechtfertigen.

## HTML-Bericht

1. **Abschließende Empfehlung**: einführen, nicht einführen oder unzureichende Belege; einschließlich geeigneter und ungeeigneter Szenarien.
2. **Wert und Nutzen**: Ergebnisqualität, gesamte Bearbeitungszeit, Token, Kosten, Schritte, Fehler und Wiederholungen.
3. **Aufrufnachweis**: Im letzten Abschnitt werden Befehle, Tool-Aufrufe, Ein- und Ausgaben, Logs, Zeitstempel, Task-IDs und Status beider Methoden getrennt gespeichert.

Nicht verfügbare Metriken erscheinen als „Nicht verfügbar“, nie als null. Geheimnisse müssen entfernt werden.

## Installation

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

Oder Repository klonen und gemäß der Skill-Verzeichnisregel des verwendeten Agenten installieren:

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git
```

## Beispiel

```text
Nutze Capability Value Test, um meine bisherige Browser-Methode mit der Methode nach Integration von Lightpanda zu vergleichen. Zeige mir zuerst den Versuchsplan.
```

## Bericht manuell erzeugen

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

Der Renderer nutzt nur die Python-Standardbibliothek und erzeugt eine einzelne offline nutzbare HTML-Datei.

Die aktuelle Version verwendet ein festes, versioniertes Berichtsformat. Jeder Bericht behält dieselben Abschnitte und dieselbe Reihenfolge bei und erklärt jeden Hauptabschnitt direkt unter seiner Überschrift. Die Standardsprache entspricht der Gesprächssprache des Nutzers und kann oben rechts gewechselt werden. Die Analyse trennt Versuchsergebnisse, belegte externe Recherche und die abschließende Empfehlung und beschreibt Einsatzszenarien anhand konkreter Nutzer, Aufgaben und Umgebungen.

## Grenzen

- Ein Lauf pro Methode liefert richtungsweisende Belege, keine statistische Garantie.
- Beide Methoden müssen dieselbe repräsentative Aufgabe erledigen können.
- Token und Kosten werden nur verglichen, wenn der Host sie bereitstellt.
- Ist der Aufruf nicht nachweisbar, muss das Ergebnis „Unzureichende Belege“ lauten.
- Headless-Ausführung wird als Protokoll gezeigt, nicht als Live-Aufzeichnung.

## Lizenz

Derzeit ist keine Lizenzdatei enthalten. Ein öffentliches Repository gewährt nicht automatisch das Recht, das Projekt zu kopieren, zu ändern oder weiterzugeben.
