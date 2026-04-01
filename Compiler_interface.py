import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import messagebox
import Compilador 
import Parser

# ================= CONFIGURAÇÃO GLOBAL =================

root = tk.Tk()
root.title("Compilador")
root.geometry("1400x850")
root.configure(bg="#f4f6fb")

# Estilo para a Tabela (Treeview)
style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview", 
                background="white", 
                foreground="#2d3436", 
                fieldbackground="white", 
                rowheight=35,
                borderwidth=0)
style.configure("Treeview.Heading", 
                background="#f1f3f9", 
                foreground="#2d3436", 
                font=("Segoe UI", 10, "bold"),
                borderwidth=0)

# ================= CORES E CONSTANTES =================

SIDEBAR_BG = "#ffffff"
CARD_BG = "#ffffff"
HOVER_BG = "#f0f4ff"  
PRIMARY = "#4a6cf7"
TEXT = "#2d3436"
BORDER = "#e3e6ef"
MISMATCH_BG = "#fE6e6e"

# ================= LÓGICA DE HOVER SINCRONIZADO =================

def on_enter(card, label_titulo, label_contador):
    # Altera todos os elementos simultaneamente
    card.configure(bg=HOVER_BG)
    label_titulo.configure(bg=HOVER_BG)
    label_contador.configure(bg="#dee7ff") 

def on_leave(card, label_titulo, label_contador):
    # Retorna ao estado original
    card.configure(bg=CARD_BG)
    label_titulo.configure(bg=CARD_BG)
    label_contador.configure(bg="#eef2ff")

# ================= FUNÇÃO CRIAR CARD =================

def criar_card(parent, titulo, contador, comando):
    card = tk.Frame(
        parent,
        bg=CARD_BG,
        padx=20,
        pady=15,
        highlightthickness=1,
        highlightbackground=BORDER,
        cursor="hand2"
    )
    card.pack(fill="x", padx=15, pady=8)

    titulo_label = tk.Label(
        card,
        text=titulo,
        bg=CARD_BG,
        fg=TEXT,
        font=("Segoe UI", 11, "bold") # Corrigido de semibold para bold
    )
    titulo_label.pack(side="left")

    contador_label = tk.Label(
        card,
        text=contador,
        bg="#eef2ff",
        fg=PRIMARY,
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=4
    )
    contador_label.pack(side="right")

    # BINDINGS CENTRALIZADOS
    # Usamos o evento do Card para controlar os filhos, evitando o "duplo hover"
    card.bind("<Enter>", lambda e: on_enter(card, titulo_label, contador_label))
    card.bind("<Leave>", lambda e: on_leave(card, titulo_label, contador_label))
    
    # Evento de clique
    card.bind("<Button-1>", lambda e: comando())
    
    # Propaga o clique dos labels para a função de comando
    titulo_label.bind("<Button-1>", lambda e: comando())
    contador_label.bind("<Button-1>", lambda e: comando())

    return contador_label

# ================= ESTRUTURA DE LAYOUT =================

container = tk.Frame(root, bg="#f4f6fb")
container.pack(fill="both", expand=True)

sidebar = tk.Frame(container, bg=SIDEBAR_BG, width=300)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar, 
    text="COMPILADOR", 
    bg=SIDEBAR_BG, 
    fg=PRIMARY, 
    font=("Segoe UI", 16, "bold"),
    pady=40
).pack()

content = tk.Frame(container, bg="#f4f6fb")
content.pack(side="right", fill="both", expand=True, padx=25, pady=20)

# FRAMES
frame_codigo = tk.Frame(content, bg="#f4f6fb")
frame_lexico = tk.Frame(content, bg="#f4f6fb")
frame_simbolos = tk.Frame(content, bg="#f4f6fb")
frame_sintatico = tk.Frame(content, bg="#f4f6fb")
frame_semantico = tk.Frame(content, bg="#f4f6fb")

frames = [frame_codigo, frame_lexico, frame_simbolos, frame_sintatico, frame_semantico]

def mostrar(frame):
    for f in frames: f.pack_forget()
    frame.pack(fill="both", expand=True)

label_linhas = criar_card(sidebar, "Código Fonte", "0 linhas", lambda: mostrar(frame_codigo))
label_tokens = criar_card(sidebar, "Análise Léxica", "0 tokens", lambda: mostrar(frame_lexico))
label_simbolos = criar_card(sidebar, "Símbolos", "0 Símbolos", lambda: mostrar(frame_simbolos))
label_erros = criar_card(sidebar, "Análise Sintática", "0 erros", lambda: mostrar(frame_sintatico))
label_identificadores = criar_card(sidebar, "Análise Semântica", "0 nós", lambda: mostrar(frame_semantico))

# ================= TOPBAR =================

topbar = tk.Frame(content, bg="#f4f6fb")
topbar.pack(fill="x", pady=(0, 20))

def criar_botao_topo(texto, primary=False, command=None):
    bg_col = PRIMARY if primary else CARD_BG
    fg_col = "white" if primary else TEXT
    
    btn = tk.Label(
        topbar,
        text=texto,
        bg=bg_col,
        fg=fg_col,
        font=("Segoe UI", 10, "bold"),
        padx=20,
        pady=8,
        cursor="hand2",
        highlightthickness=1 if not primary else 0,
        highlightbackground=BORDER
    )
    btn.pack(side="left", padx=5)
    
    # Adiciona o evento de clique se um comando for fornecido
    if command:
        btn.bind("<Button-1>", lambda e: command())
    
    if not primary:
        btn.bind("<Enter>", lambda e: btn.config(bg="#f8f9fa"))
        btn.bind("<Leave>", lambda e: btn.config(bg=CARD_BG))
    else:
        btn.bind("<Enter>", lambda e: btn.config(bg="#3a5bd9"))
        btn.bind("<Leave>", lambda e: btn.config(bg=PRIMARY))
    return btn

def compilar():
    mismatchs = []

    codigo = text_area.get("1.0", "end-1c")

    compilador = Compilador.Compilador()

    compilador.tokens = list(compilador.lexer.analise(codigo))

    tokens = compilador.tokens

    label_tokens.config(text=f"{len(tokens)} tokens")

    for i in tabela_lexica.get_children():
        tabela_lexica.delete(i)
    
    for i in tabela_erros.get_children():
        tabela_erros.delete(i)
    
    for tok in tokens:
        if tok.type not in {"MISMATCH", "MISMATCH_numero_inteiro", "MISMATCH_identificador", "comentario_bloco_incompleto"}:
            tabela_lexica.insert("", "end", values=(
                tok.type,
                tok.lexeme,
                tok.line,
                tok.col_start,
                tok.col_end
            ))
        else:
            mismatchs.append(tok)
    
    for erro in mismatchs:
        tabela_erros.insert("", "end", values=(
            erro.lexeme,
            erro.line,
            erro.col_start,
            erro.col_end
        ), tags=("mismatch",))

    try:
        symbols = compilador.compile(codigo)
        for i in tabela_simbolos.get_children():
            tabela_simbolos.delete(i)

        label_simbolos.config(text=f"{len(symbols.symbols)} símbolos")

        for sym in symbols.symbols:
            tabela_simbolos.insert("", "end", values=(sym.name, sym.type, sym.category, sym.value, sym.passed_as, sym.used, sym.lexical_level, sym.scope),)

        label_erros.config(text="0 erros")

    except SyntaxError as erro:
        label_erros.config(text="1 erro")
        print("Erro sintático:", erro)

    mostrar(frame_lexico)

def novo():
    text_area.delete("1.0", "end")
    label_linhas.config(text="0 linhas")
    label_tokens.config(text="0 tokens")
    label_erros.config(text="0 erros")
    for i in tabela_lexica.get_children():
        tabela_lexica.delete(i)
    mostrar(frame_codigo)

criar_botao_topo("Novo", command=novo)


def import_text():
    arquivo = filedialog.askopenfilename(
        title="Selecionar arquivo",
        filetypes=[("Arquivos de Texto", "*.txt")]
    )

    if arquivo:
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()

            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, conteudo)
            atualizar_contadores()
            mostrar(frame_codigo)

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo.\n{e}")

criar_botao_topo("Abrir", command=import_text)

# criar_botao_topo("Salvar")
btn_run = criar_botao_topo("Compilar", primary=True, command=compilar)
btn_run.pack(side="right")

# ================= EDITOR =================

editor_container = tk.Frame(frame_codigo, bg="white", highlightthickness=1, highlightbackground=BORDER)
editor_container.pack(fill="both", expand=True)

text_area = tk.Text(
    editor_container,
    font=("Consolas", 12),
    bd=0,
    padx=20,
    pady=20,
    insertbackground=PRIMARY,
    selectbackground="#dbe4ff"
)
text_area.pack(fill="both", expand=True)

def atualizar_contadores(event=None):
    linhas = int(text_area.index('end-1c').split('.')[0])
    label_linhas.config(text=f"{linhas} linhas")

text_area.bind("<KeyRelease>", atualizar_contadores)

# ================= TABELA =================

# scrollbar = ttk.Scrollbar(frame_lexico, orient="vertical")
# scrollbar.pack(side="right", fill="y")

tabela_lexica = ttk.Treeview(
    frame_lexico,
    columns=("Tipo", "Lexema", "Linha", "Coluna Inicial", "Coluna Final"),
    show="headings",
    # yscrollcommand=scrollbar.set
)
# scrollbar.config(command=tabela_lexica.yview)
for col in tabela_lexica["columns"]:
    tabela_lexica.heading(col, text=col.upper())
    tabela_lexica.column(col, width=120, anchor="center")
tabela_lexica.pack(fill="both", expand=True)

label_erros = tk.Label(frame_lexico, text="ERROS ENCONTRADOS", bg=MISMATCH_BG, fg="white", font=("Segoe UI", 14, "bold"), pady=10)
label_erros.pack(fill="x", pady=(10, 0))
scrollbar_erros = ttk.Scrollbar(frame_lexico, orient="vertical")
scrollbar_erros.pack(side="right", fill="y")

tabela_erros = ttk.Treeview(
    frame_lexico,
    columns=("Lexema", "Linha", "Coluna Inicial", "Coluna Final"),
    show="headings",
    yscrollcommand=scrollbar_erros.set
)
scrollbar_erros.config(command=tabela_erros.yview)

for col in tabela_erros["columns"]:
    tabela_erros.heading(col, text=col.upper())
    tabela_erros.column(col, width=120, anchor="center")
tabela_erros.pack(fill="both", expand=True)

tabela_simbolos = ttk.Treeview(
    frame_simbolos,
    columns=("símbolo", "tipo", "categoria", "valor", "passado como", "usado", "nível léxico", "escopo"),
    show="headings"
)
for col in tabela_simbolos["columns"]:
    tabela_simbolos.heading(col, text=col.upper())
    tabela_simbolos.column(col, width=120, anchor="center")
tabela_simbolos.pack(fill="both", expand=True)

mostrar(frame_codigo)
root.mainloop()