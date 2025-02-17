import sqlite3

# connessione al database
# serve un database sull'alphabot per fare funzioni più complicate

conn = sqlite3.connect('db_comandi.db')  # mi connetto al database
cur = conn.cursor()

query_crea = ''' 
                create table "Comandi"( 
                "tasto" VARCHAR(1) NOT NULL, 
                "str_mov" TEXT NOT NULL,
                PRIMARY KEY ("tasto"));
            '''
cur.execute(query_crea)
conn.commit()  
# str_mov ha la sintassi per i movimenti (F50,L40,B20)
# pk ha il tasto associato

query_popola = '''
                INSERT INTO Comandi ("tasto", "str_mov") VALUES
                ("q", "C_90_SX;FX;LX"),
                ("e", "C_90_DX;FX;RX"),
                ("z", "C_180_SX;FX;LX"),
                ("c", "C_180_DX,FX;RX")
                '''
cur.execute(query_popola)
conn.commit()

query_select = '''
                SELECT * 
                FROM Comandi
                '''
cur.execute(query_select)
variabile_stampa = cur.fetchall()
# conn.close()
