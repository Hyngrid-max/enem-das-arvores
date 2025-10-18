#!/usr/bin/env python3
\"\"\"Enem com Árvores - Protótipo mínimo (Python + Tkinter)
Features included:
- OOP structure (Jogador, Arvore, Missao, MiniGame base)
- Simple GUI with menu, act map, mission screen
- One mini-game: "Ritual de Plantio" (sequence memory)
- Save/load progress (JSON)
Run: python enem_arvores_prototipo.py
\"\"\"

import tkinter as tk
from tkinter import messagebox, simpledialog
import json, random, os

SAVE_FILE = 'enem_arvores_save.json'

# ======= Models =======
class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.pontos = {\"linguagens\":0, \"humanas\":0, \"exatas\":0, \"biologicas\":0}
        self.progress = {\"atos_concluidos\":0}
    def ganhar_pontos(self, area, valor):
        if area in self.pontos:
            self.pontos[area] += valor

class Arvore:
    def __init__(self, especie='Ancestral'):
        self.especie = especie
        self.idade = 0
        self.saude = 100
    def diminuir_saude(self, v): self.saude = max(0, self.saude - v)
    def melhorar_saude(self, v): self.saude = min(100, self.saude + v)

class Missao:
    def __init__(self, titulo, descricao, disciplina):
        self.titulo = titulo
        self.descricao = descricao
        self.disciplina = disciplina
        self.concluida = False
    def concluir(self, jogador):
        self.concluida = True
        jogador.ganhar_pontos(self.disciplina, 10)

# ======= MiniGame Base and a Memory Sequence mini-game =======
class MiniGame:
    def __init__(self, master, on_complete):
        self.master = master
        self.on_complete = on_complete
    def start(self): raise NotImplementedError

class RitualDePlantio(MiniGame):
    COLORS = ['red','green','blue','yellow']
    def __init__(self, master, on_complete):
        super().__init__(master, on_complete)
        self.sequence = []
        self.user_index = 0
        self.level = 1
        self.frame = tk.Frame(master)
    def start(self):
        self.frame.pack(fill='both', expand=True)
        tk.Label(self.frame, text=\"Ritual de Plantio - memorize a sequência\", font=('Arial',14)).pack(pady=8)
        self.buttons_frame = tk.Frame(self.frame)
        self.buttons_frame.pack(pady=10)
        self.buttons = {}
        for c in self.COLORS:
            b = tk.Button(self.buttons_frame, bg=c, width=8, height=4,
                          command=lambda color=c: self.press(color))
            b.pack(side='left', padx=5)
            self.buttons[c]=b
        self.info = tk.Label(self.frame, text=\"Nível 1 - pressione 'Iniciar' para ver a sequência\")
        self.info.pack(pady=8)
        ctrl = tk.Frame(self.frame)
        ctrl.pack()
        tk.Button(ctrl, text='Iniciar', command=self.next_round).pack(side='left', padx=6)
        tk.Button(ctrl, text='Sair', command=self.end_game).pack(side='left', padx=6)
    def flash(self, color):
        btn = self.buttons[color]
        orig = btn['relief']
        btn.config(relief='sunken')
        self.frame.update()
        self.frame.after(350)
        btn.config(relief=orig)
        self.frame.update()
    def show_sequence(self):
        for color in self.sequence:
            self.frame.after(300, lambda c=color: self.flash(c))
            self.frame.update()
            self.frame.after(500)
    def next_round(self):
        # extend sequence and show it
        self.sequence.append(random.choice(self.COLORS))
        self.user_index = 0
        self.info.config(text=f\"Nível {self.level}: observe a sequência\")
        self.frame.update()
        # show with delays
        self._show_with_delay(0)
    def _show_with_delay(self, i):
        if i >= len(self.sequence):
            self.info.config(text=f\"Sua vez (reproduza a sequência).\")
            return
        color = self.sequence[i]
        self.flash(color)
        self.frame.after(400, lambda: self._show_with_delay(i+1))
    def press(self, color):
        if not self.sequence:
            self.info.config(text=\"Pressione Iniciar para ver a sequência.\")
            return
        expected = self.sequence[self.user_index]
        if color == expected:
            self.user_index +=1
            if self.user_index == len(self.sequence):
                # level up
                self.level +=1
                self.info.config(text=f\"Acertou! Próximo nível: {self.level}\")
                self.on_complete(success=True, reward=5)  # immediate small reward
            else:
                self.info.config(text=f\"Ok {self.user_index}/{len(self.sequence)}\")
        else:
            self.info.config(text=f\"Erro! Sequência reiniciada. Nível atingido: {self.level}\")
            self.sequence = []
            self.level = 1
            self.on_complete(success=False, reward=0)
    def end_game(self):
        self.frame.destroy()
        self.on_complete(success=False, reward=0)

# ======= Persistence =======
def save_progress(jogador, arvore):
    data = {'jogador': {'nome':jogador.nome, 'pontos':jogador.pontos, 'progress':jogador.progress},
            'arvore': {'especie':arvore.especie, 'idade':arvore.idade, 'saude':arvore.saude}}
    with open(SAVE_FILE,'w', encoding='utf-8') as f:
        json.dump(data,f, indent=2)
def load_progress():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE,'r', encoding='utf-8') as f:
        data = json.load(f)
    jogador = Jogador(data['jogador']['nome'])
    jogador.pontos = data['jogador']['pontos']
    jogador.progress = data['jogador'].get('progress', {'atos_concluidos':0})
    arvore = Arvore(data['arvore'].get('especie','Ancestral'))
    arvore.idade = data['arvore'].get('idade',0)
    arvore.saude = data['arvore'].get('saude',100)
    return jogador, arvore

# ======= GUI App =======
class App:
    def __init__(self, root):
        self.root = root
        root.title(\"Enem com Árvores - Protótipo\")
        root.geometry('700x450')
        self.jogador = None
        self.arvore = None
        self.current_frame = None
        self.build_menu()
    def build_menu(self):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill='both', expand=True)
        tk.Label(self.current_frame, text=\"Enem com Árvores\", font=('Helvetica',18,'bold')).pack(pady=10)
        tk.Button(self.current_frame, text=\"Novo Jogo\", width=20, command=self.novo_jogo).pack(pady=6)
        tk.Button(self.current_frame, text=\"Carregar Jogo\", width=20, command=self.carregar_jogo).pack(pady=6)
        tk.Button(self.current_frame, text=\"Mapa dos Atos\", width=20, command=self.mapa_atos).pack(pady=6)
        tk.Button(self.current_frame, text=\"Salvar Progresso\", width=20, command=self.salvar).pack(pady=6)
        tk.Button(self.current_frame, text=\"Sair\", width=20, command=self.root.quit).pack(pady=6)
    def novo_jogo(self):
        nome = simpledialog.askstring(\"Nome\", \"Digite seu nome de jogador:\", parent=self.root)
        if not nome: return
        self.jogador = Jogador(nome)
        self.arvore = Arvore()
        messagebox.showinfo(\"Bem-vindo\", f\"Bem-vindo, {nome}!\")
    def carregar_jogo(self):
        res = load_progress()
        if res is None:
            messagebox.showinfo(\"Carregar\", \"Nenhum save encontrado.\")
            return
        self.jogador, self.arvore = res
        messagebox.showinfo(\"Carregado\", f\"Jogo carregado: {self.jogador.nome}\")
    def salvar(self):
        if not self.jogador or not self.arvore:
            messagebox.showwarning(\"Salvar\", \"Nenhum progresso para salvar.\")
            return
        save_progress(self.jogador, self.arvore)
        messagebox.showinfo(\"Salvar\", \"Progresso salvo com sucesso.\")
    def mapa_atos(self):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill='both', expand=True)
        tk.Label(self.current_frame, text=\"Mapa dos Atos (Protótipo)\", font=('Arial',14)).pack(pady=8)
        atos = [\"Ato 0: Tutorial - Plantio\", \"Ato 1: Colonização\", \"Ato 2: Crescimento Científico\",
               \"Ato 3: Comunidade\", \"Ato 4: Industrialização\", \"Ato 5: Ruína / Restauração\"]
        for i, a in enumerate(atos):
            f = tk.Frame(self.current_frame)
            f.pack(fill='x', padx=20, pady=4)
            tk.Label(f, text=a).pack(side='left')
            tk.Button(f, text='Iniciar', command=lambda idx=i: self.iniciar_ato(idx)).pack(side='right')
        tk.Button(self.current_frame, text='Voltar', command=self.build_menu).pack(pady=10)
    def iniciar_ato(self, idx):
        # For prototype, starting any ato goes to a sample missão with mini-game
        if self.jogador is None:
            messagebox.showwarning(\"Sem jogador\", \"Crie ou carregue um jogador primeiro.\")
            return
        missao = Missao(titulo=f\"Missão do Ato {idx}\", descricao=\"Resolver o Ritual de Plantio\", disciplina='exatas')
        self.show_missao(missao)
    def show_missao(self, missao):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill='both', expand=True)
        tk.Label(self.current_frame, text=missao.titulo, font=('Arial',14,'bold')).pack(pady=6)
        tk.Message(self.current_frame, text=missao.descricao, width=600).pack(pady=6)
        tk.Button(self.current_frame, text='Iniciar Mini-game', command=lambda: self.start_minigame(missao)).pack(pady=6)
        tk.Button(self.current_frame, text='Voltar ao mapa', command=self.mapa_atos).pack(pady=6)
    def start_minigame(self, missao):
        # launch RitualDePlantio inside the main window; handle completion
        def on_complete(success, reward):
            if success:
                messagebox.showinfo(\"Mini-game\", f\"Mini-game concluído! +{reward} pontos (exatas).")
                self.jogador.ganhar_pontos('exatas', reward)
                missao.concluir(self.jogador)
            else:
                messagebox.showinfo(\"Mini-game\", \"Mini-game terminou (sem recompensa).")
            # after completion, return to map
            self.mapa_atos()
        mg = RitualDePlantio(self.root, on_complete)
        # destroy current_frame then start mg
        if self.current_frame: self.current_frame.destroy()
        mg.start()

# ======= Run =======
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
