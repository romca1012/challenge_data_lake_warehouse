#!/bin/bash
set -e

# Valeur par défaut si PY_FILE n'est pas défini
PY_SCRIPT=${PY_FILE:-simulate_producer.py}

echo "📦 Démarrage du script Python : $PY_SCRIPT"
python "/app/$PY_SCRIPT"
