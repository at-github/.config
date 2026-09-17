---
description: Supprimer une ou des sessions opencode (par extrait de titre ou ID)
agent: build
---

Sessions opencode connues :
!`opencode session list --format json`

Demande : $ARGUMENTS

Consignes d'exécution :
1. Ne JAMAIS supprimer la session dans laquelle tu t'exécutes actuellement.
2. Relire la liste injectée ci-dessus ; cibler la/les session(s) correspondant à la demande :
   - ID exact (`ses_...`) ou extrait du titre (ex: "504", "PR"), positionné dans $ARGUMENTS.
   - Sans argument : afficher la liste complète (ID, titre, dossier, dates de mise à jour)
     et laisser l'utilisateur choisir le(s) session(s) à supprimer par numéro ou ID.
3. Afficher les sessions ciblées (ID + titre) et demander confirmation avant toute suppression.
4. Supprimer chaque session avec : opencode session delete <ID>
5. Après suppression, afficher la liste restante des sessions pour validation visuelle.
