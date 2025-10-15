# Sistema di Entanglement Automatico

Sistema per generare automaticamente combinazioni creative tra i tuoi interessi, con esecuzione schedulata su GitHub Actions.

## 🚀 Setup Veloce

### 1. Crea Repository GitHub
```bash
# Nella cartella entanglement-system/
git init
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/TUO_USERNAME/entanglement-system.git
git branch -M main
git push -u origin main
```

### 2. Abilita Permessi Write
- Settings → Actions → General
- Workflow permissions → "Read and write permissions" ✅

### 3. Test
- Actions → "Auto Entanglement" → Run workflow

## 📝 Modifica Interessi

Edita `interessi.json`:
```json
{
  "interessi": ["giardinaggio", "elettronica", "fotografia", "cucina"]
}
```

Poi:
```bash
git add interessi.json
git commit -m "Aggiornato interessi"
git push
```

## ⏰ Schedulazione

Default: ogni giorno ore 9:00 UTC

Modifica in `.github/workflows/entanglement.yml`:
```yaml
- cron: '0 21 * * *'  # 21:00 UTC = 22:00 Italia
```

## 📊 Output

- `combinazioni_generate.json` - snapshot corrente
- `storia_entanglement.jsonl` - storico completo

## 🔄 Integrazione con Claude

```
Analizza combinazioni_generate.json e per ogni combinazione fornisci:
1. Nome descrittivo
2. 3-5 applicazioni concrete
3. 2-3 idee innovative  
4. Livello difficoltà

Ordina per: potenziale mercato, facilità, originalità.
Output JSON.
```
