import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
import matplotlib.pyplot as plt

class BaseStationSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator Stacji Bazowej")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        self.running = False
        self.start_time = 0
        self.stats = {"served": 0, "rejected": 0, "total_wait": 0, "queue_history": [], "rho_history": [], "wait_history": []}
        self.channels = []
        self.queue = []

        self.setup_ui()

    def setup_ui(self):
        # Panel parametrów
        params_frame = ttk.LabelFrame(self.root, text="Parametry wejściowe")
        params_frame.pack(padx=10, pady=5, fill="x")

        # Konfiguracja siatki
        for i in range(4): params_frame.columnconfigure(i, weight=1)

        labels = [
            ("Liczba kanałów:", "channels_count", "10"),
            ("λ (Intensywność ruchu):", "lambda_val", "0.5"),
            ("N (Średnia rozmowa):", "avg_call", "10.0"),
            ("σ (Odchylenie std):", "sigma_val", "2.0"),
            ("Min. długość rozmowy:", "min_call", "1.0"),
            ("Max. długość rozmowy:", "max_call", "30.0"),
            ("Długość kolejki:", "max_queue", "5"),
            ("Czas symulacji (s):", "sim_time", "60")
        ]

        self.entries = {}
        row, col = 0, 0
        for text, var_name, default in labels:
            ttk.Label(params_frame, text=text).grid(row=row, column=col, padx=5, pady=2, sticky="e")
            ent = ttk.Entry(params_frame, width=10)
            ent.insert(0, default)
            ent.grid(row=row, column=col+1, padx=5, pady=2, sticky="w")
            self.entries[var_name] = ent
            col += 2
            if col > 2:
                col = 0
                row += 1

        self.btn_start = ttk.Button(params_frame, text="Uruchom symulację", command=self.start_simulation)
        self.btn_start.grid(row=row, column=0, columnspan=4, pady=10)

        # Panel statusu
        status_frame = ttk.Frame(self.root)
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.lbl_time = ttk.Label(status_frame, text="Czas: 0.0s", font=("Courier", 12, "bold"), width=15)
        self.lbl_time.pack(side="left")
        
        self.lbl_served = ttk.Label(status_frame, text="Obsłużeni: 0", font=("Courier", 12), width=20)
        self.lbl_served.pack(side="left")

        # Panel kanałów i kolejki
        display_frame = ttk.Frame(self.root)
        display_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Sekcja Kanałów
        ttk.Label(display_frame, text="Status kanałów:").pack(anchor="w")
        self.canvas_channels = tk.Canvas(display_frame, height=150, bg="white", highlightthickness=1)
        self.canvas_channels.pack(fill="x", pady=5)

        # Sekcja Kolejki ze Scrollbarem
        ttk.Label(display_frame, text="Kolejka oczekujących:").pack(anchor="w")
        q_container = ttk.Frame(display_frame)
        q_container.pack(fill="both", expand=True)
        
        self.tree_queue = ttk.Treeview(q_container, columns=("ID", "WaitTime"), show="headings", height=8)
        self.tree_queue.heading("ID", text="ID Rozmowy")
        self.tree_queue.heading("WaitTime", text="Czas oczekiwania [s]")
        self.tree_queue.column("ID", width=100, anchor="center")
        self.tree_queue.column("WaitTime", width=200, anchor="center")
        
        scrollbar = ttk.Scrollbar(q_container, orient="vertical", command=self.tree_queue.yview)
        self.tree_queue.configure(yscrollcommand=scrollbar.set)
        
        self.tree_queue.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_inputs(self):
        try:
            p = {k: float(v.get()) for k, v in self.entries.items()}
            if p['sim_time'] <= 1: raise ValueError
            if any(v <= 0 for v in [p['lambda_val'], p['avg_call'], p['sigma_val'], p['min_call'], p['max_call']]):
                raise ValueError
            return p
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne wartości dodatnie. Czas symulacji > 1s.")
            return None

    def start_simulation(self):
        params = self.validate_inputs()
        if not params: return

        self.btn_start.config(state="disabled")
        self.running = True
        self.start_time = time.time()
        self.channels = [{"busy": False, "remaining": 0.0} for _ in range(int(params['channels_count']))]
        self.queue = []
        self.stats = {"served": 0, "rejected": 0, "total_wait": 0, "queue_history": [], "rho_history": [], "wait_history": []}
        
        threading.Thread(target=self.sim_loop, args=(params,), daemon=True).start()

    def sim_loop(self, p):
        duration = p['sim_time']
        next_arrival = random.expovariate(p['lambda_val'])
        elapsed = 0
        last_tick = time.time()

        while elapsed < duration and self.running:
            dt = time.time() - last_tick
            last_tick = time.time()
            elapsed = time.time() - self.start_time

            # Obsługa przychodzącego połączenia
            if elapsed >= next_arrival:
                call_len = max(p['min_call'], min(p['max_call'], random.gauss(p['avg_call'], p['sigma_val'])))
                
                # Szukaj wolnego kanału
                assigned = False
                for ch in self.channels:
                    if not ch["busy"]:
                        ch["busy"] = True
                        ch["remaining"] = round(float(call_len), 2)
                        assigned = True
                        self.stats["served"] += 1
                        break
                
                if not assigned:
                    if len(self.queue) < p['max_queue']:
                        self.queue.append({"len": round(float(call_len), 2), "start": elapsed})
                    else:
                        self.stats["rejected"] += 1
                
                next_arrival += random.expovariate(p['lambda_val'])

            # Aktualizacja kanałów
            busy_count = 0
            for ch in self.channels:
                if ch["busy"]:
                    ch["remaining"] -= dt
                    busy_count += 1
                    if ch["remaining"] <= 0:
                        if self.queue:
                            next_call = self.queue.pop(0)
                            wait_time = elapsed - next_call["start"]
                            self.stats["total_wait"] += wait_time
                            ch["remaining"] = next_call["len"]
                            self.stats["served"] += 1
                        else:
                            ch["busy"] = False
                            ch["remaining"] = 0.0

            # Mierzenie statystyk
            rho = busy_count / p['channels_count']
            self.stats["rho_history"].append(rho)
            self.stats["queue_history"].append(len(self.queue))
            avg_w = self.stats["total_wait"] / self.stats["served"] if self.stats["served"] > 0 else 0
            self.stats["wait_history"].append(avg_w)

            self.root.after(0, self.update_ui, elapsed, self.stats["served"])
            time.sleep(0.05)

        self.root.after(0, self.finish_simulation, p)

    def update_ui(self, elapsed, served):
        self.lbl_time.config(text=f"Czas: {elapsed:.1f}s")
        self.lbl_served.config(text=f"Obsłużeni: {served}")
        
        # Rysowanie kanałów
        self.canvas_channels.delete("all")
        w = 40
        for i, ch in enumerate(self.channels):
            color = "red" if ch["busy"] else "green"
            x0 = 10 + i * (w + 5)
            self.canvas_channels.create_rectangle(x0, 20, x0+w, 70, fill=color)
            val = f"{ch['remaining']:.1f}" if ch["busy"] else "IDLE"
            self.canvas_channels.create_text(x0+w/2, 85, text=val, font=("Arial", 8))
            self.canvas_channels.create_text(x0+w/2, 10, text=str(i+1))

        # Aktualizacja listy kolejki
        for item in self.tree_queue.get_children():
            self.tree_queue.delete(item)
        for i, q_item in enumerate(self.queue):
            wait = time.time() - self.start_time - q_item["start"]
            self.tree_queue.insert("", "end", values=(f"Rozmowa {i+1}", f"{wait:.2f}"))

    def finish_simulation(self, p):
        self.running = False
        self.btn_start.config(state="normal")
        self.save_results(p)
        self.show_plots()
        messagebox.showinfo("Koniec", "Symulacja zakończona. Wyniki zapisano do pliku.")

    def save_results(self, p):
        filename = "wyniki_symulacji.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("PARAMETRY SYMULACJI\n")
            for k, v in p.items():
                f.write(f"{k}: {v}\n")
            f.write(f"Łącznie obsłużonych: {self.stats['served']}\n")
            f.write(f"Łącznie odrzuconych: {self.stats['rejected']}\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Sekunda':<10} | {'ρ (Intensywność)':<20} | {'Q (Kolejka)':<15} | {'W (Czekanie)':<15}\n")
            f.write("-" * 50 + "\n")
            
            for i in range(len(self.stats["rho_history"])):
                if i % 20 == 0: # Pomiar co około sekundę
                    sec = i // 20
                    rho = f"{self.stats['rho_history'][i]:.3f}"
                    q = f"{self.stats['queue_history'][i]}"
                    w = f"{self.stats['wait_history'][i]:.3f}"
                    f.write(f"{sec:<10} | {rho:<20} | {q:<15} | {w:<15}\n")

    def show_plots(self):
        fig, axs = plt.subplots(3, 1, figsize=(8, 10))
        plt.subplots_adjust(hspace=0.4)

        axs[0].plot(self.stats["rho_history"], color='blue')
        axs[0].set_title("ρ - Intensywność ruchu w czasie")
        axs[0].set_ylabel("Obciążenie")

        axs[1].plot(self.stats["queue_history"], color='orange')
        axs[1].set_title("Q - Średnia długość kolejki")
        axs[1].set_ylabel("Liczba oczekujących")

        axs[2].plot(self.stats["wait_history"], color='green')
        axs[2].set_title("W - Średni czas oczekiwania")
        axs[2].set_ylabel("Sekundy")

        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseStationSimulator(root)
    root.mainloop()