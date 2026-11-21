# Capability Value Test｜Validation de la valeur d’une nouvelle capacité

[English](README.md)｜[简体中文](README.zh-CN.md)｜[繁體中文](README.zh-TW.md)｜[日本語](README.ja.md)｜[한국어](README.ko.md)｜[Русский](README.ru.md)｜[हिन्दी](README.hi.md)｜[Español](README.es.md)｜**Français**｜[Deutsch](README.de.md)｜[Português](README.pt.md)｜[العربية](README.ar.md)

> Rendre visible l’utilisation d’une nouvelle capacité et mesurable la valeur qu’elle crée.

Capability Value Test est un Skill générique pour les agents d’IA. Il vérifie si une capacité nouvellement intégrée (Skill, modèle, plugin, MCP Server, navigateur, composant open source ou workflow d’agent) a réellement été utilisée et si elle crée une valeur mesurable par rapport à la méthode précédente.

Il conçoit un test A/B équitable entre la méthode précédente et celle rendue possible par la nouvelle capacité. Par défaut, il utilise trois tâches représentatives issues du travail habituel de l’utilisateur ou d’exemples fournis. Un humain examine le protocole complet avant toute exécution. Le résultat est un rapport HTML autonome, visuel et traçable.

## Questions traitées

1. **La capacité a-t-elle réellement été utilisée et où se trouve la preuve ?**
2. **A-t-elle créé de la valeur et peut-on la quantifier ?**
3. **Le processus d’utilisation et la valeur concrète sont-ils compréhensibles visuellement ?**

## Déroulement

1. Définir la nouvelle capacité et les méthodes avant et après son intégration.
2. Choisir trois tâches représentatives du travail habituel de l’utilisateur.
3. Conserver les mêmes entrées, exigences de sortie, règles d’arrêt et critères d’évaluation à chaque manche.
4. Soumettre le protocole complet à un humain et le réviser s’il est refusé.
5. Après approbation explicite, exécuter les deux méthodes pendant trois manches et enregistrer résultats, métriques et preuves.
6. Analyser les écarts et générer le rapport HTML.

L’objectif n’est pas de faire gagner la nouvelle capacité, mais de déterminer ce qui change et si les preuves justifient son adoption.

## Rapport HTML

1. **Résumé de décision** : présente d’abord les deux méthodes, la conclusion, la raison principale, la question de valeur et la date.
2. **Comparaison et analyse** : affiche les données agrégées des trois manches, les résultats par manche, les observations, les sources externes, les avantages, les limites, les scénarios concrets et les incertitudes.
3. **Conception et preuves** : explique le choix des tâches, les conditions équitables et les critères. Chaque manche ouvre deux chronologies ; appels de modèles, outils et journaux bruts sont joints à l’étape où ils se sont produits.

Une métrique absente est indiquée « Indisponible », jamais remplacée par zéro. Les secrets doivent être supprimés.

## Installation

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

Ou clonez le dépôt et suivez la convention de répertoire Skill de votre agent :

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git
```

## Exemple d’utilisation

```text
Utilise Capability Value Test pour comparer ma méthode de navigation actuelle avec celle rendue possible par Lightpanda. Présente d’abord le protocole.
```

## Génération manuelle du rapport

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

Le générateur utilise uniquement la bibliothèque standard Python et produit un fichier HTML unique utilisable hors ligne.

La dernière version utilise un format de rapport fixe et versionné. Tous les rapports conservent les mêmes sections et le même ordre, avec une explication sous chaque titre principal. La langue par défaut correspond à la langue de conversation de l’utilisateur et peut être changée en haut à droite. L’analyse distingue les résultats de l’expérience, les recherches externes citées et la recommandation finale, puis décrit chaque scénario par un utilisateur, une tâche et un environnement concrets.

## Limites

- Trois tâches représentatives réduisent l’effet du hasard, mais ne donnent qu’une indication limitée à ces tâches.
- À chaque manche, les deux méthodes doivent utiliser la même entrée et les mêmes critères.
- Les Token et les coûts ne sont comparés que si l’hôte les fournit.
- Si l’utilisation ne peut pas être vérifiée, la conclusion doit être « Preuves insuffisantes ».
- Une exécution headless est présentée comme un journal, jamais comme un enregistrement en direct.

## Licence

Le projet est publié sous [licence MIT](LICENSE).
