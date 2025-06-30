# Pipeline de Données Temps Réel - Projet Smart City

## Présentation

Ce projet simule un pipeline de données temps réel pour une ville intelligente. On suit un véhicule qui va de Londres à Birmingham et on génère différentes données en temps réel (vitesse, incidents, météo, trafic…). Ces données sont envoyées dans Kafka, traitées avec Spark, stockées dans AWS S3, puis visualisées avec Power BI.

## Architecture (vue simplifiée)

- Les données sont simulées depuis un script Python.
- Elles sont envoyées dans des topics Kafka via Docker.
- Spark lit les données depuis Kafka, les traite, puis les écrit au format Parquet dans S3.
- Glue les référence, et on peut les interroger avec Athena.
- Enfin, on utilise Power BI pour créer des dashboards.

## Technologies utilisées

- **Kafka + Zookeeper** : ingestion temps réel
- **Spark Streaming** : traitement en flux
- **Docker** : conteneurisation de l’environnement
- **AWS S3, Glue, Athena** : stockage, catalogue et interrogation
- **Python** : génération et traitement des données
- **Power BI** : visualisation des données

## Étapes principales

1. Lancer l’environnement avec Docker (Kafka + Spark).
2. Exécuter le simulateur Python pour envoyer les données dans Kafka.
3. Lancer le job Spark pour lire, traiter et stocker les données dans S3.
4. Utiliser Glue et Athena pour interroger les données.
5. Connecter Power BI à Athena ou S3 pour construire le tableau de bord.

## Exemples de visualisations Power BI

- Vitesse moyenne par zone
- Carte des trajets
- Incidents détectés
- Évolution des conditions météo
- Densité du trafic

## Pré-requis

- Docker / Docker Compose
- Compte AWS configuré (avec droits sur S3, Glue, Athena)
- Python 3.x installé
- Power BI Desktop

## Objectif

Ce projet montre comment simuler et analyser des données de ville connectée en temps réel, depuis l’ingestion jusqu’à la visualisation.

