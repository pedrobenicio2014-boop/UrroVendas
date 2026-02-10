import sqlite3

# Conecta ao banco (se não existir, ele cria o arquivo automaticamente)
conn = sqlite3.connect('dados.db')
cursor = conn.cursor()

# Cria uma tabela simples de exemplo
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER
    )
''')

# Insere um dado inicial para teste
cursor.execute("INSERT INTO usuarios (nome, idade) VALUES ('Pedro', 25)")

conn.commit()
conn.close()
print("Banco de dados 'dados.db' criado com sucesso!")
