#!/usr/bin/env python3
"""
Sistema di Entanglement Automatico per Interessi
Genera combinazioni creative e le salva con timestamp
"""

import json
import itertools
from datetime import datetime
from pathlib import Path

class InterestEntangler:
    def __init__(self, interests_file="interessi.json", output_file="combinazioni_generate.json"):
        self.interests_file = Path(interests_file)
        self.output_file = Path(output_file)
        self.history_file = Path("storia_entanglement.jsonl")
        
    def load_interests(self):
        """Carica gli interessi dal file JSON"""
        with open(self.interests_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['interessi']
    
    def save_interests(self, interests):
        """Salva gli interessi aggiornati"""
        data = {
            "interessi": interests,
            "ultima_modifica": datetime.now().isoformat(),
            "ultima_elaborazione": datetime.now().isoformat()
        }
        with open(self.interests_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_combinations(self, interests):
        """Genera tutte le possibili combinazioni (2, 3, ... n elementi)"""
        combinations = []
        for r in range(2, len(interests) + 1):
            for combo in itertools.combinations(interests, r):
                combinations.append(list(combo))
        return combinations
    
    def save_combinations(self, combinations):
        """Salva le combinazioni generate"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "totale_combinazioni": len(combinations),
            "combinazioni": combinations
        }
        
        # Salva output corrente
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Appendi alla storia (JSONL = una riga JSON per esecuzione)
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(output, ensure_ascii=False) + '\n')
    
    def add_interest(self, new_interest):
        """Aggiungi un nuovo interesse"""
        interests = self.load_interests()
        if new_interest not in interests:
            interests.append(new_interest)
            self.save_interests(interests)
            return True
        return False
    
    def remove_interest(self, interest):
        """Rimuovi un interesse"""
        interests = self.load_interests()
        if interest in interests:
            interests.remove(interest)
            self.save_interests(interests)
            return True
        return False
    
    def run_entanglement(self):
        """Esegui il processo di entanglement completo"""
        print("🔄 Avvio entanglement...")
        
        interests = self.load_interests()
        print(f"📚 Interessi caricati: {len(interests)}")
        
        if len(interests) < 2:
            print("⚠️  Servono almeno 2 interessi per generare combinazioni")
            return
        
        combinations = self.generate_combinations(interests)
        print(f"✨ Generate {len(combinations)} combinazioni")
        
        self.save_combinations(combinations)
        self.save_interests(interests)  # Aggiorna timestamp elaborazione
        
        print(f"💾 Salvate in: {self.output_file}")
        print(f"📜 Storia aggiornata in: {self.history_file}")
        
        return combinations


def main():
    entangler = InterestEntangler()
    
    # Esegui entanglement
    combinations = entangler.run_entanglement()
    
    if combinations:
        print("\n📋 Prime 5 combinazioni:")
        for combo in combinations[:5]:
            print(f"  • {' + '.join(combo)}")


if __name__ == "__main__":
    main()
