Questo progetto è un sistema di gestione ordini basato su Telegram, sviluppato in Python utilizzando il framework Aiogram.
Il bot consente ai clienti di consultare un catalogo prodotti, filtrato per categoria, ed effettuare ordini in modo guidato tramite pulsanti interattivi.
Gli ordini vengono notificati in tempo reale al venditore, che può gestirli direttamente da Telegram.

Il sistema è pensato per piccole attività commerciali, venditori locali o attività che necessitano di un canale di ordinazione semplice, immediato e sempre accessibile.


Architettura del sistema
	•	Bot Telegram (interfaccia utente)
	•	Aiogram (async) per la gestione degli eventi
	•	SQLite come database persistente
	•	Fly.io per il deploy e l’esecuzione 24/7
	•	Volume persistente per conservare i dati anche dopo i riavvii



Cliente
	•	Avvio interazione con /start
	•	Selezione categoria di prodotti
	•	Visualizzazione prodotti disponibili per categoria
	•	Ordine guidato tramite pulsanti (nessun input manuale complesso)
	•	Inserimento quantità con validazione
	•	Conferma ordine

Venditore
	•	Visualizzazione ordini ricevuti
	•	Informazioni complete su:
	•	prodotto
	•	quantità
	•	nome cliente
	•	Possibilità di confermare o rifiutare l’ordine (logica pronta per estensione)