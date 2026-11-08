# Leva: ripristino del motore e allineamento al riferimento

## Stato attuale

Il motore completo è ripristinato. B attiva lo stato della leva soltanto a
terra e vicino alla leva visibile, non più nella zona vuota d'ingresso.
Il punto osservato è approssimativamente (29,63) nella vista 12 e (73,149)
nella vista 13. Le due proiezioni concordano con la traslazione misurata
(+44,+86) di assets/lever_route_manifest.json. Le coordinate sono una scelta
manuale sul riferimento; il raggio di interazione di 24 pixel è provvisorio.
I fotogrammi originali sono reference/w1l1_next/178.png e 180.png.

Viene rimosso il limite invisibile a x=130 dell'area 12 introdotto dal prototipo
Copilot: impediva di raggiungere la leva prima dell'apertura e non deriva
dal terreno osservato. Il portale 12→13 è nuovamente percorribile senza
attivazione. La parete rocciosa sinistra dell'area 13 resta solida.

Lo stato lever_activated/barrier_open sopravvive a morte e rivisita, mentre R
lo cancella insieme alla partita. barrier_open rappresenta soltanto lo stato
logico futuro: non dimostra una barriera fisica originale integrata.
Non sono implementati animazione originale, barriera mobile di spine e
percorso successivo. I pixel della leva nel fondale restano statici.
Nessun nuovo livello è completo e la stima resta al 14,5%.

## Verifiche

I test controllano la raggiungibilità prima dell'attivazione, entrambe le
proiezioni della leva, pressione nuova di B, pulsante già mantenuto, azioni
lontane o aeree, ritorni, morte/reset, guardia e gemme persistenti.
La regressione mGBA raggiunge le due viste con i pulsanti, sconfigge la guardia,
si avvicina alla leva visibile e preme B. Legge telemetria di sola osservazione
per verificare attivazione e conservazione dopo il ritorno; non scrive coordinate.

## Cronologia

Il commit eadca9a aveva sostituito src/game.c con sole due funzioni statiche.
Il ripristino f76b989 ha riabilitato il motore e corretto la pressione di B.
Il checkpoint a9ce7fd superava i test ma manteneva una zona di interazione
e un limite d'ingresso provvisori non allineati alla leva originale.
Questo aggiornamento sostituisce quel comportamento e i relativi test.
I risultati GitHub di quel checkpoint non vengono attribuiti alla nuova ROM.

## Risultati locali dell'allineamento

Quindici test C con ASan/UBSan e quattro test Python superati. Atlante
riproducibile verificato e ROM compilata con GCC ARM 13.2.1. La regressione
mGBA 0.10.2 termina con successo: 5.176 aggiornamenti presentati in 5.176
fotogrammi attivi delle aree 1–13. Anche la riapertura SRAM con nuovi core passa.
Nessuna verifica su hardware reale viene dichiarata.
