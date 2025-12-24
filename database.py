import sqlite3

# In database.py
DB_NAME = "/data/shop.db" # Percorso assoluto nel volume

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prodotti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    quantita INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    prezzo REAL NOT NULL
);
                
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ordini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nome_cliente TEXT NOT NULL,
    prodotto TEXT NOT NULL,
    quantita INTEGER NOT NULL,
    stato TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
    """)

    conn.commit()
    conn.close()


def get_prodotti(categoria):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT nome, quantita, categoria, prezzo FROM prodotti WHERE categoria = ?", (categoria,))
    rows = cur.fetchall()

    conn.close()
    return rows

def get_categorie ():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT categoria FROM prodotti")
    result = cur.fetchall()
    
    conn.close()
    return result is not None

def prodotto_esiste(nome):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM prodotti WHERE nome = ?", (nome,))
    result = cur.fetchone()

    conn.close()
    return result is not None

def crea_ordine(user_id, nomecliente, prodotto, quantita):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ordini (user_id, nome_cliente, prodotto, quantita, stato)
        VALUES (?, ?, ?, ?, 'pending')
    """, (user_id, nomecliente, prodotto, quantita))

    ordine_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ordine_id


def get_ordini_pending():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, user_id, nome_cliente, prodotto, quantita
        FROM ordini
        WHERE stato = 'pending'
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def conferma_ordine(ordine_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ordini SET stato = 'confirmed'
        WHERE id = ?
    """, (ordine_id,))

    conn.commit()
    conn.close()


def annulla_ordine(ordine_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ordini SET stato = 'cancelled'
        WHERE id = ?
    """, (ordine_id,))

    conn.commit()
    conn.close()


def scala_quantita(prodotto, quantita):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE prodotti
        SET quantita = quantita - ?
        WHERE nome = ?
    """, (quantita, prodotto))

    conn.commit()
    conn.close()

def seed_prodotti():
    prodotti = [
        ("mele", 50, "40K", "15"),
        ("banane", 30, "40K", "15"),
        ("arance", 20, "60K", "20"),
        ("pere", 15, "60K", "20")
    ]

    conn = get_connection()
    cur = conn.cursor()

    for nome, quantita, categoria, prezzo in prodotti:
        cur.execute(
            "INSERT OR IGNORE INTO prodotti (nome, quantita, categoria, prezzo) VALUES (?, ?, ?, ?)",
            (nome, quantita, categoria, prezzo)
        )

    conn.commit()
    conn.close()