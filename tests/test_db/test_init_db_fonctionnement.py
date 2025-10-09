"""
Triggers

Vérifier que le trigger set_updated_at existe pour :

utilisateur

conversation

personnageIA

Vérifier qu’une mise à jour d’une ligne change bien updated_at.

Tests de cascade / intégrité

Supprimer un utilisateur → vérifier que ses :

session

conversation (et messages associés)

liens dans conv_utilisateur et persoIA_utilisateur
sont supprimés.

Supprimer une conversation → vérifier que ses messages sont supprimés.

Supprimer un personnageIA → vérifier que les liens dans persoIA_utilisateur sont supprimés (si cascade définie).

Insérer un utilisateur, un personnageIA, une conversation et un message → récupérer et vérifier que les valeurs sont correctes.

Tester que les DEFAULT (created_at, updated_at) sont bien remplis automatiquement.
"""