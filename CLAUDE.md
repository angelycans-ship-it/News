# News — Rassegna stampa mattutina

Questo repository ospita la rassegna stampa mattutina dell'utente, pubblicata
tramite GitHub Pages a partire da `index.html` sul branch `main`.

## Passaggio fisso: aggiornare `main` ogni giorno

Ogni volta che viene generata una nuova edizione della rassegna (scheduled
task giornaliero):

1. Sviluppare e committare come di consueto sul branch dedicato della sessione
   (`claude/...`).
2. **Autorizzazione permanente**: dopo il commit sul branch dedicato, fare
   push diretto (fast-forward) anche su `main`, così il sito GitHub Pages
   mostra sempre l'edizione del giorno. L'utente ha confermato esplicitamente
   che questo passaggio è autorizzato in modo permanente e NON richiede
   conferma ad ogni esecuzione: `git push origin <sha-o-branch-locale>:main`.
3. Se il push su `main` non risultasse un fast-forward pulito (conflitti),
   fermarsi e chiedere conferma all'utente invece di forzare o riscrivere la
   storia.

File coinvolti in ogni edizione: `index.html` (servito da GitHub Pages) e
`template.html` (riferimento di design, stessa struttura/CSS, solo contenuti
aggiornati).
