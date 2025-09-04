-----------------------------------------------------
-- Utilisateur
-----------------------------------------------------
DROP TABLE IF EXISTS utilisateur CASCADE ;
CREATE TABLE utilisateur(
    id_utilisateur    SERIAL PRIMARY KEY,
    prenom       VARCHAR(30) UNIQUE,
    nom          VARCHAR(30) UNIQUE,
    mdp          VARCHAR(256),
    naiss        DATE,
    mail         VARCHAR(50)
);
