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

def get_users ():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT nome_cliente FROM ordini")
    result = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return result


def get_prodotti(categoria=None):
    conn = get_connection()
    cur = conn.cursor()

    if categoria is None:
        cur.execute("SELECT nome, quantita, categoria, prezzo FROM prodotti ORDER BY categoria, nome")
    else:
        cur.execute(
            "SELECT nome, quantita, categoria, prezzo FROM prodotti WHERE categoria = ? AND quantita > 0 ORDER BY nome",
            (categoria,)
        )

    result = cur.fetchall()
    conn.close()
    return result

def get_categorie ():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT categoria,prezzo FROM prodotti")
    result = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return result

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
        INSERT INTO ordini (user_id, nome_cliente, prodotto, quantita, stato, timestamp)
        VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
    """, (user_id, nomecliente, prodotto, quantita))

    ordine_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ordine_id


def get_ordini (user_id=None):
    conn = get_connection()
    cur = conn.cursor()

    if user_id is None:
        cur.execute("""
            SELECT id, user_id, nome_cliente, prodotto, quantita, stato, timestamp
            FROM ordini
            """)
    else:
        cur.execute("""
            SELECT id, user_id, nome_cliente, prodotto, quantita, stato, timestamp
            FROM ordini
            WHERE user_id = ?
            """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

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
    prodotti = []

    conn = get_connection()
    cur = conn.cursor()

    for nome, quantita, categoria, prezzo in prodotti:
        cur.execute(
            "INSERT INTO prodotti (nome, quantita, categoria, prezzo) VALUES (?, ?, ?, ?)",
            (nome, quantita, categoria, prezzo)
        )

    conn.commit()
    conn.close()