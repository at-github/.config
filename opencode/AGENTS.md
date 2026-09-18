# AGENTS.md - Guide pour les agents de développement

## Préférences utilisateur

### Analyse

- Demander des clarifications pour toute ambiguïté
- En cas de demande impliquant beaucoup de modifications, proposer un plan en étapes.
  - Présenter le plan (ou l'approche) en mode plan et attendre la validation de l'utilisateur avant d'exécuter / de modifier le code
  - Pendant la conception du plan, analyser les risques de régressions
  - Ces étapes devraient être testables
  - Ces étapes ne doivent pas contenir régression
  - Ces étapes devraient être autonome et ne pas dépendre d'une prochaine étape dans la mesure du possible
  - Avant un remaniement ou un déplacement de code, identifier les tests existants qui
    alerteraient d'une régression ; si aucun n'existe, les écrire d'abord et vérifier qu'ils
    passent sur le code actuel avant de le modifier
  - Avancer les étapes une par une : l'utilisateur relit et vérifie le code à chaque étape
    avant de commiter lui même et de passer à la suivante
- Garder les plans concis : privilégier les décisions, l'architecture et les tests, plutôt que des
  détails fragiles (numéros de lignes, tailles de fichiers, listes exhaustives par fichier) qui
  deviennent vite obsolètes. Les points concrets à modifier sont identifiés au moment du code.
- Éviter de dupliquer la logique : rechercher et cibler les points d'entrée communs
  (ex: un chokepoint partagé par plusieurs chemins) avant d'ajouter des appels à plusieurs endroits.
- Code mort : même si appelé par les tests.
- Le dépôt peut changer pendant un échange (commit, stash, checkout effectués par l'utilisateur).
  Avant toute réponse portant sur l'état du code, ou avant toute modification, vérifier
  `git status --short` + `git rev-parse HEAD` et comparer avec la référence du dernier échange
  (pour les questions hors code : `git rev-parse HEAD` seul). En cas d'écart, relire le code
  concerné avant de répondre, et le signaler seulement si l'écart peut affecter la demande.

### Exécution

- Lancer les tests associés après chaque modification
- Ne jamais committer, ni push, ni effectuer de `git add` (stage).
  Laisser les fichiers modifiés tels quels ; l'utilisateur relit, puis prépare et valide lui-même les commits.

## Prérequis avant toute intervention

Avant de lire, créer ou modifier un fichier, vérifier qu'un `README.md` existe dans :
- Le dossier du fichier concerné
- Les dossiers parents immédiats (jusqu'à la racine du module)
- Préviens moi si un fichier `README.md` n'est pas présent

Si il existe lire le `README.md` en premier — sans exception. Il peut contenir :
- Le rôle du module
- Son utilité dans l'architecture
- Les conventions spécifiques au dossier

Ne pas lister les fichiers du dossier dans un README : cette liste devient vite
obsolète et fragile. Décrire le rôle et les responsabilités, pas l'inventaire.
