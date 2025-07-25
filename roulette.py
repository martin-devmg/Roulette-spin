# Importation des bibliothèques nécessaires
import tkinter as tk
from tkinter import messagebox, simpledialog
import math
import random
import datetime

# Dictionnaire associant chaque chiffre à une couleur
COLOR_MAP = {
    0: "#3498db",
    1: "#2ecc71",
    2: "#f1c40f",
    5: "#9b59b6",
    8: "#1abc9c",
    10: "#e74c3c"
}

# Liste des chiffres affichés sur la roue
NUMBERS = [0, 1, 2, 5, 8, 10] * 6
TOTAL_PARTS = len(NUMBERS)
ANGLE_PER_PART = 360 / TOTAL_PARTS

class RouletteApp:
    def __init__(self, master):
        """
        Initialise la fenêtre, configure les composants graphiques et demande le montant initial au joueur.
        Crée également un fichier historique pour enregistrer les mises gagnées et perdues.
        """
        self.master = master
        self.master.title("🎰 Roulette 🎰")
        self.master.state("zoomed")  # Plein écran
        self.master.configure(bg="#1e1e2e")

        # Demande du montant initial au joueur
        self.balance = simpledialog.askinteger("Montant initial", "Veuillez entrer le montant initial (MGA) :", minvalue=1000, initialvalue=10000)
        if not self.balance:
            self.balance = 10000  # Valeur par défaut si annulation

        self.angle_offset = 0  # Décalage de l'angle de départ
        self.is_spinning = False  # Indicateur de spin en cours

        # Création/écrasement du fichier d'historique
        self.history_file = open("historique_roulette.txt", "w", encoding="utf-8")
        self.history_file.write(f"=== HISTORIQUE DE PARTIE - {datetime.datetime.now()} ===\n")

        # Canvas de la roue
        self.canvas = tk.Canvas(master, width=500, height=500, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Label d'entrée de mise
        self.bet_label = tk.Label(master, text="Entrez votre mise :", font=("Segoe UI", 14), bg="#1e1e2e", fg="white")
        self.bet_label.pack(pady=(10, 0))

        # Champ de saisie de mise
        self.bet_entry = tk.Entry(master, font=("Segoe UI", 16), justify="center")
        self.bet_entry.pack()

        # Label affichant le solde
        self.balance_label = tk.Label(master, text=f"💰 Solde: {self.balance} MGA", font=("Segoe UI", 16), bg="#1e1e2e", fg="white")
        self.balance_label.pack(pady=10)

        # Label affichant le résultat
        self.result_label = tk.Label(master, text="", font=("Segoe UI", 16), bg="#1e1e2e", fg="white")
        self.result_label.pack(pady=10)

        # Bouton pour lancer la roue
        self.spin_button = tk.Button(master, text="🎲 Tourner", font=("Segoe UI", 16, "bold"), bg="#2ecc71", fg="white", relief="flat", command=self.start_spin)
        self.spin_button.pack(pady=10)

        self.create_wheel()

    def create_wheel(self):
        """
        Dessine la roue sur le canvas en fonction de l'angle offset actuel.
        Chaque segment est coloré selon le chiffre et affiche le numéro correspondant.
        """
        self.canvas.delete("all")
        start_angle = self.angle_offset
        for number in NUMBERS:
            extent = ANGLE_PER_PART
            color = COLOR_MAP[number]
            self.canvas.create_arc(50, 50, 450, 450, start=start_angle, extent=extent, fill=color, outline="black")
            mid_angle = math.radians(start_angle + extent / 2)
            x = 250 + 150 * math.cos(mid_angle)
            y = 250 - 150 * math.sin(mid_angle)
            self.canvas.create_text(x, y, text=str(number), fill="white", font=("Segoe UI", 12, "bold"))
            start_angle += extent
        # Flèche blanche en haut indiquant l'endroit où la roue s'arrête
        self.canvas.create_polygon([245, 10, 255, 10, 250, 40], fill="white")

    def start_spin(self):
        """
        Valide la mise entrée par l'utilisateur et lance l'animation de rotation si la mise est correcte.
        Empêche le lancement multiple si un spin est déjà en cours.
        """
        if self.is_spinning:
            return
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide.")
            return
        if bet <= 0 or bet > self.balance:
            messagebox.showerror("Erreur", "Mise invalide ou solde insuffisant.")
            return
        self.is_spinning = True
        self.spin_speed = 30  # Vitesse de rotation initiale
        self.spin_duration = random.randint(60, 100)  # Durée de rotation aléatoire
        self.bet = bet
        self.animate_spin(0)

    def animate_spin(self, step):
        """
        Anime la roue en la faisant tourner et ralentir progressivement
        jusqu'à l'arrêt complet où le résultat sera déterminé.
        """
        if step < self.spin_duration:
            self.angle_offset = (self.angle_offset + self.spin_speed) % 360
            self.create_wheel()
            self.spin_speed = max(1, self.spin_speed - 0.4)  # ralentissement progressif
            self.master.after(40, lambda: self.animate_spin(step + 1))
        else:
            self.determine_result()

    def determine_result(self):
        """
        Détermine le chiffre gagnant selon l'angle final de la roue,
        calcule le gain ou la perte, met à jour le solde et enregistre l'historique.
        """
        adjusted_angle = (270 - self.angle_offset) % 360
        index = int(adjusted_angle // ANGLE_PER_PART) % TOTAL_PARTS
        result = NUMBERS[index]

        if result == 0:
            self.balance -= self.bet
            self.result_label.config(text=f"😢 Perdu {self.bet} MGA | Résultat: {result}", fg="red")
            self.history_file.write(f"Perdu {self.bet} MGA | Résultat: {result}\n")
        else:
            gain = self.bet * result
            self.balance += gain - self.bet
            self.result_label.config(text=f"🎉 Gagné {gain} MGA | Résultat: {result}", fg="lime")
            self.history_file.write(f"Gagné {gain} MGA | Résultat: {result}\n")

        self.balance_label.config(text=f"💰 Solde: {self.balance} MGA")

        if self.balance <= 0:
            messagebox.showinfo("Fin de partie", "💥 Vous n'avez plus d'argent. Fin du jeu.")
            self.history_file.write("=== FIN DE PARTIE ===\n")
            self.history_file.close()
            self.master.destroy()
        self.is_spinning = False

    def on_closing(self):
        """
        Ferme proprement le fichier d'historique avant de fermer la fenêtre
        si l'utilisateur quitte le jeu manuellement.
        """
        self.history_file.write("=== FIN DE PARTIE (FERMETURE MANUELLE) ===\n")
        self.history_file.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()