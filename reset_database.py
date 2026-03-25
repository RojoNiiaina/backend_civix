#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line
from django.conf import settings

# Supprimer la base de données existante
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print("✅ Base de données supprimée")

# Supprimer les migrations problématiques
migrations_to_remove = [
    'apps/reports/migrations/0002_remove_report_category_id_report_category.py',
    'apps/reports/migrations/0003_remove_report_category_remove_report_latitude_and_more.py'
]

for migration in migrations_to_remove:
    if os.path.exists(migration):
        os.remove(migration)
        print(f"✅ Migration supprimée: {migration}")

# Recréer les migrations
print("🔄 Création des nouvelles migrations...")
execute_from_command_line(['manage.py', 'makemigrations'])
execute_from_command_line(['manage.py', 'migrate'])
print("✅ Base de données recréée avec succès!")
