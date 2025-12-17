"""
Script d'initialisation de la base de données
Crée les tables et insère 10 produits exemples
"""
import sys
from app import app, db, logger
from models import Product
from datetime import datetime

def init_database():
    """Initialise la base de données avec le schéma et les données exemples"""
    
    with app.app_context():
        try:
            # Créer toutes les tables
            logger.info('Création des tables de la base de données...')
            db.create_all()
            print('✅ Tables créées avec succès')
            
            # Vérifier si des produits existent déjà
            existing_count = Product.query.count()
            if existing_count > 0:
                logger.info(f'{existing_count} produits déjà présents dans la base')
                print(f'ℹ️  {existing_count} produits déjà présents - ignorant l\'insertion')
                return
            
            # Produits exemples à insérer
            sample_products = [
                {
                    'name': 'MacBook Pro 16"',
                    'price': 2899.99,
                    'category': 'Ordinateurs'
                },
                {
                    'name': 'iPhone 15 Pro',
                    'price': 1299.00,
                    'category': 'Smartphones'
                },
                {
                    'name': 'AirPods Pro',
                    'price': 279.00,
                    'category': 'Audio'
                },
                {
                    'name': 'iPad Air',
                    'price': 699.00,
                    'category': 'Tablettes'
                },
                {
                    'name': 'Apple Watch Series 9',
                    'price': 449.00,
                    'category': 'Montres'
                },
                {
                    'name': 'Magic Keyboard',
                    'price': 129.00,
                    'category': 'Accessoires'
                },
                {
                    'name': 'Magic Mouse',
                    'price': 89.00,
                    'category': 'Accessoires'
                },
                {
                    'name': 'Studio Display',
                    'price': 1799.00,
                    'category': 'Écrans'
                },
                {
                    'name': 'HomePod Mini',
                    'price': 109.00,
                    'category': 'Audio'
                },
                {
                    'name': 'Mac Mini M2',
                    'price': 699.00,
                    'category': 'Ordinateurs'
                }
            ]
            
            logger.info(f'Insertion de {len(sample_products)} produits exemples...')
            print(f'📦 Insertion de {len(sample_products)} produits...')
            
            # Insérer chaque produit
            for i, product_data in enumerate(sample_products, 1):
                product = Product.from_dict(product_data)
                
                # Valider avant insertion
                is_valid, message = product.validate()
                if not is_valid:
                    logger.error(f'Validation échouée pour {product_data["name"]}: {message}')
                    print(f'❌ Erreur: {message}')
                    continue
                
                db.session.add(product)
                print(f'   {i}. {product_data["name"]} - {product_data["price"]}€')
            
            # Commit de toutes les insertions
            db.session.commit()
            
            # Vérifier le nombre de produits insérés
            total_products = Product.query.count()
            logger.info(f'Base de données initialisée avec {total_products} produits')
            print(f'\n✅ Base de données initialisée avec succès!')
            print(f'📊 Total: {total_products} produits')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Erreur lors de l\'initialisation: {str(e)}', exc_info=True)
            print(f'\n❌ Erreur lors de l\'initialisation: {str(e)}')
            sys.exit(1)

if __name__ == '__main__':
    print('🚀 Initialisation de la base de données...\n')
    init_database()
