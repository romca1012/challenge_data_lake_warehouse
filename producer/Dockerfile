FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer les packages Python avec versions spécifiques
RUN pip install --no-cache-dir \
    confluent-kafka==2.4.0 \
    py4j==0.10.9.7 \
    pyspark==3.5.1 \
    simplejson==3.19.2

# Copier le code de l'application
COPY . /app

# Copier et rendre exécutable l'entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Définir l'entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Commande par défaut (modifiable via entrypoint ou docker run)
CMD ["simulate_producer.py"]
