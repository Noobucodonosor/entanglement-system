# `vehicle.json` — dati d'officina Symphony ST 200i

Scheda macchina-leggibile del SYM Symphony ST 200i ABS Euro 4 (motore XB20E2-EU),
trascritta dalla scheda d'officina ScooterLab v1.0 (agosto 2026).

Serve come sorgente unica di soglie e coppie per il monitoraggio: i valori qui
dentro sono quelli con cui si tarano gli allarmi, non un promemoria da leggere.

## Regola di trascrizione

**Nessun valore e' stimato o dedotto.** Ogni dato che il manuale non fornisce e'
`null`, con la posizione in cui cercarlo registrata in `open_questions`.
Se un campo e' `null`, il codice a valle deve trattarlo come "soglia non
disponibile" e non come zero.

I campi `_note` accanto ai numeri conservano il contesto che rende il numero
utilizzabile (condizioni di misura, fonte, perche' due fonti divergono).

## Le due correzioni rispetto ai dati precedenti

1. **Cinghia: sostituzione a 12.000 km, non a 6.000.** Il valore vecchio veniva
   da una tabella di gamma SYM che contiene la riga *Carburetor (idle speed)* —
   e' la tabella del 50 a carburatore, non del 200 a iniezione. Ispezione a
   1.000 / 3.000 / 6.000 km, sostituzione a 12.000. I rulli non hanno alcun
   intervallo fisso: solo pulizia, controllo e sostituzione se necessario.
   Conseguenza: la manutenzione programmata costa circa la meta' di quanto
   stimato prima.
2. **Minimo a 1.800 ± 100 rpm, non 1.700.** Il service manual USA (Fiddle III)
   dice 1.700 ± 100, ma la scheda SYM Italia dell'XB20E2-EU Euro 4 specifica
   1.800 ± 100. In `engine.idle_rpm` vale la taratura italiana; quella USA
   resta in `engine.idle_rpm.alternate`.

## Il numero che rende il progetto autosufficiente

`cvt.belt.width_service_limit_mm = 17.5` (nuova: 19,7 mm → 2,2 mm di vita utile).

E' un riferimento fisico assoluto: misura la larghezza col calibro a ogni
apertura del carter e registrala insieme ai km e all'indice di slittamento.
Dopo due o tre punti hai la curva di usura reale del tuo mezzo e prevedi la
sostituzione con settimane di anticipo, invece di seguire una scadenza scritta
a Taiwan.

## ABS — vincolo non negoziabile

L'anello fonico e' un disco separato imbullonato al disco freno su entrambe le
ruote, quindi ispezionabile a pinza smontata. Il segnale dei sensori si deriva
**in parallelo ad alta impedenza**: mai interrompere il collegamento
sensore ↔ centralina, mai iniettare nulla sulla linea. L'ABS e' omologato e deve
continuare a funzionare identico. Nel dubbio si montano i magneti come da piano
originale — si perde risoluzione, non sicurezza. Il vincolo e' codificato in
`abs.tapping_rule`.

Restano da verificare fisicamente due cose, mezz'ora sul mezzo: il tipo di
sensore (2 fili → probabilmente passivo induttivo; 3 fili → attivo con
alimentazione) e il numero di denti dell'anello fonico, che determina la
risoluzione.

## Cosa manca

Vedi `open_questions`: limite di usura rulli, limiti masse frizione e campana,
lunghezza libera della molla della puleggia condotta, tolleranze
cilindro/pistone, alzate camme, capitolo ABS completo. Stanno nei capitoli
centrali dei manuali (il Jet 14 supera i 30 MB e viene troncato in lettura
automatica). Recuperati quei valori, si aggiornano i `null` e diventano soglie
di allarme.

## Uso

```python
import json
v = json.load(open("tools/vehicle.json"))

limite = v["cvt"]["belt"]["width_service_limit_mm"]   # 17.5
coppia = v["torques_nm"]["variator_nut"]              # {'thread': 'M12', 'min': 49, 'max': 59, ...}

rulli = v["cvt"]["rollers"]["diameter_service_limit_mm"]
if rulli is None:
    ...  # soglia non disponibile: non trattare come 0
```
