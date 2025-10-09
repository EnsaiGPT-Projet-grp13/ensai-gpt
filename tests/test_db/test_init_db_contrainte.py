 
 class TestContrainteDB():
    def test_mail_unique():
        pass

    def test_nom_persoIA_unique():
        pass

 """   Clés primaires

Vérifier que chaque table a sa clé primaire définie.

b) Clés étrangères

personnageIA.created_by → référence utilisateur(id_utilisateur)

session.id_utilisateur → référence utilisateur(id_utilisateur) avec ON DELETE CASCADE

conversation.id_proprio → référence utilisateur(id_utilisateur) avec ON DELETE CASCADE

conversation.id_personnageIA → référence personnageIA(id_personnageIA)

message.id_conversation → référence conversation(id_conversation) avec ON DELETE CASCADE

message.id_utilisateur → référence utilisateur(id_utilisateur)

conv_utilisateur.id_utilisateur → référence utilisateur(id_utilisateur) avec ON DELETE CASCADE

conv_utilisateur.id_conversation → référence conversation(id_conversation) avec ON DELETE CASCADE

persoIA_utilisateur.id_utilisateur → référence utilisateur(id_utilisateur) avec ON DELETE CASCADE

persoIA_utilisateur.id_personnageIA → référence personnageIA(id_personnageIA) avec ON DELETE CASCADE

c) Contraintes uniques

utilisateur.mail doit être unique.

personnageIA.name doit être unique.

d) Not Null

Vérifier que toutes les colonnes NOT NULL n’acceptent pas NULL.

e) Check constraints

message.expediteur doit être 'utilisateur' ou 'IA'

temperature, top_p, max_tokens → accepter des valeurs numériques valides.

is_collab, is_public → accepter seulement des booléens.

expediteur → rejeter toute valeur autre que 'utilisateur' ou 'IA'.

mail → tester qu’une valeur non email passe quand même (PostgreSQL n’impose pas de format par défaut, donc juste vérifier insertion possible).
"""