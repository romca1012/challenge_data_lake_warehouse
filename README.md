# Pipeline de Données Temps Réel - Projet Smart City

## Présentation

Ce projet simule un pipeline de données temps réel pour une ville intelligente. On suit un véhicule allant de Londres à Birmingham et on génère différentes données en temps réel (vitesse, incidents, météo, trafic…). Ces données sont envoyées dans Kafka, traitées avec Spark, stockées dans **HDFS via Hive**, puis visualisées avec Power BI.

## Architecture (vue simplifiée)

- Les données sont simulées depuis un script Python.
- Elles sont envoyées dans des topics Kafka via Docker.
- Spark lit les données depuis Kafka, les traite, puis les écrit au format Parquet dans **HDFS**.
- Hive permet de référencer ces données et de les interroger en SQL.
- Enfin, on utilise Power BI pour créer des dashboards à partir des tables Hive.

## Technologies utilisées

- **Kafka + Zookeeper** : ingestion temps réel
- **Spark Structured Streaming** : traitement en flux
- **HDFS + Hive Metastore** : stockage et catalogue de données
- **Docker / Docker Compose** : orchestration de l’environnement local
- **Python** : génération et traitement des données
- **Power BI** : visualisation des données

## Étapes principales

1. Lancer l’environnement complet avec Docker (Kafka, Hive, Spark, HDFS).
2. Exécuter le simulateur Python (`main.py`) pour injecter des données dans Kafka.
3. Lancer le job Spark pour lire, traiter et stocker les données dans HDFS.
4. Vérifier les tables Hive créées (via Beeline ou Hue si configuré).
5. Connecter Power BI à Hive ou aux fichiers Parquet en HDFS (via un connecteur JDBC ou un export).

## Exemples de visualisations Power BI

- Vitesse moyenne par zone
- Carte interactive des trajets
- Incidents détectés et leur évolution
- Analyse météo et conditions de circulation
- Densité du trafic par heure

## Pré-requis

- Docker / Docker Compose
- Python 3.x
- Power BI Desktop
- Environnement local compatible Hadoop (ou cluster Dockerisé fourni)
- JDBC Hive driver (pour la connexion Power BI si besoin)

## Objectif

Ce projet montre comment simuler, traiter et analyser des données de ville intelligente en temps réel, depuis l’ingestion jusqu’à la visualisation, dans un environnement big data local reposant sur l’écosystème Hadoop (Kafka, Spark, Hive, HDFS).
