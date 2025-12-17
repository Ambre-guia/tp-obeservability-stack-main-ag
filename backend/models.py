"""
Modèles de données SQLAlchemy pour la base de données PostgreSQL
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Instance SQLAlchemy partagée
db = SQLAlchemy()

class Product(db.Model):
    """
    Modèle Product représentant un produit dans la base de données
    
    Table: products
    Colonnes:
        - id: Clé primaire auto-incrémentée
        - name: Nom du produit (obligatoire)
        - price: Prix du produit en euros (obligatoire)
        - category: Catégorie du produit (obligatoire)
        - created_at: Date de création (auto-générée)
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        """Représentation string du produit"""
        return f'<Product {self.id}: {self.name}>'
    
    def to_dict(self):
        """
        Convertit l'objet Product en dictionnaire pour la sérialisation JSON
        
        Returns:
            dict: Représentation du produit en dictionnaire
        """
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crée une instance Product à partir d'un dictionnaire
        
        Args:
            data (dict): Données du produit
            
        Returns:
            Product: Instance du produit
        """
        return Product(
            name=data.get('name'),
            price=data.get('price'),
            category=data.get('category')
        )
    
    def validate(self):
        """
        Valide les données du produit
        
        Returns:
            tuple: (bool, str) - (est_valide, message_erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom du produit est obligatoire"
        
        if not self.price or self.price <= 0:
            return False, "Le prix doit être supérieur à 0"
        
        if not self.category or len(self.category.strip()) == 0:
            return False, "La catégorie est obligatoire"
        
        return True, "Validation OK"
