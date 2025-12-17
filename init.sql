-- ============================================================================
-- INITIALISATION DE LA BASE DE DONNÉES POSTGRESQL
-- Création de la table products et insertion de 10 produits exemples
-- ============================================================================

-- Créer la table products si elle n'existe pas
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

-- Insérer 10 produits exemples (vérifier qu'ils n'existent pas déjà)
INSERT INTO products (name, price, category) VALUES
    ('MacBook Pro 16"', 2899.99, 'Ordinateurs'),
    ('iPhone 15 Pro', 1299.00, 'Smartphones'),
    ('AirPods Pro', 279.00, 'Audio'),
    ('iPad Air', 699.00, 'Tablettes'),
    ('Apple Watch Series 9', 449.00, 'Montres'),
    ('Magic Keyboard', 129.00, 'Accessoires'),
    ('Magic Mouse', 89.00, 'Accessoires'),
    ('Studio Display', 1799.00, 'Écrans'),
    ('HomePod Mini', 109.00, 'Audio'),
    ('Mac Mini M2', 699.00, 'Ordinateurs')
ON CONFLICT DO NOTHING;

-- Afficher le nombre de produits insérés
DO $$
DECLARE
    product_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO product_count FROM products;
    RAISE NOTICE '✅ Table products créée avec % produits', product_count;
END $$;

-- Créer une vue pour les statistiques par catégorie
CREATE OR REPLACE VIEW products_stats AS
SELECT 
    category,
    COUNT(*) as total_products,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM products
GROUP BY category
ORDER BY total_products DESC;

-- Afficher les statistiques
SELECT * FROM products_stats;
