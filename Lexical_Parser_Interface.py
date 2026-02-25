import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import Lexical_Parser as lp
import style

# ================= JANELA =================
root = tk.Tk()
root.title("Analisador Léxico")
root.geometry("1530x1080")
root.configure(bg="#eef1f5")

janela_tabela= None

styles=style.styleConfig()

# ================= HEADER =================
header = tk.Label(
    root,
    text="ANALISADOR LÉXICO",
    bg="#1f4e79",
    fg="white",
    font=("Segoe UI", 22, "bold"),
    pady=25
)
header.pack(fill="x")

# ================= FRAME PRINCIPAL =================
main_frame = tk.Frame(root, bg="#eef1f5")
main_frame.pack(fill="both", expand=True, padx=40, pady=20)

label = tk.Label(main_frame, 
                text="Digite a expressão no espaço em branco ou importe ela de um arquivo de texto",
                fg="black",
                font=("Segoe UI", 16, "bold")
                )

label.pack(fill="x")

# ================= BOTÃO IMPORTAR =================
button_frame = tk.Frame(main_frame, bg="#eef1f5")
button_frame.pack(fill="x", pady=10)

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

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo.\n{e}")

btn_importar = ttk.Button(
    button_frame,
    text="Importar Expressão",
    command=import_text
)
btn_importar.pack()

# ================= ÁREA DE TEXTO =================
text_container = tk.Frame(
    main_frame,
    bg="white",
    bd=2,
    relief="groove"
)
text_container.pack(fill="both", pady=10)

text_frame = tk.Frame(text_container, bg="white")
text_frame.pack(fill="both", expand=True)

text_area = tk.Text(
    text_frame,
    wrap="word",
    font=("Consolas", 12),
    bd=0,
    padx=10,
    pady=8
)

scrollbar_text = ttk.Scrollbar(text_frame, command=text_area.yview)
text_area.configure(yscrollcommand=scrollbar_text.set)

text_area.pack(side="left", fill="both", expand=True)
scrollbar_text.pack(side="right", fill="y")

# ================= BOTÃO ANALISAR =================
action_frame = tk.Frame(main_frame, bg="#eef1f5")
action_frame.pack(fill="x", pady=10)

def lexical():
    content = text_area.get("1.0", "end-1c")

    if not content.strip():
        messagebox.showwarning("Aviso", "Digite ou importe um texto primeiro.")
        return

    try:
        results = list(lp.lexico(content))
        abrir_tabela(results)

    except Exception as e:
        messagebox.showerror("Erro Léxico", str(e))

btn_action = ttk.Button(action_frame, text="Analisar", command=lexical)
btn_action.pack()


def abrir_tabela(tokens):
    global janela_tabela

    if janela_tabela is not None and janela_tabela.winfo_exists():
        janela_tabela.destroy()

    janela_tabela = tk.Toplevel(root)
    janela_tabela.title("Resultado da Análise Léxica")
    janela_tabela.geometry("1530x1080")
    janela_tabela.configure(bg="#eef1f5")

    frame = tk.Frame(janela_tabela, bg="#eef1f5")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tabela = ttk.Treeview(
        frame,
        columns=("Tipo", "Lexema", "Linha", "Coluna Inicial", "Coluna Final"),
        show="headings"
    )

    tabela.heading("Tipo", text="Tipo")
    tabela.heading("Lexema", text="Lexema")
    tabela.heading("Linha", text="Linha")
    tabela.heading("Coluna Inicial", text="Coluna Inicial")
    tabela.heading("Coluna Final", text="Coluna Final")

    tabela.column("Tipo", width=150, anchor="center")
    tabela.column("Lexema", width=250)
    tabela.column("Linha", width=80, anchor="center")
    tabela.column("Coluna Inicial", width=120, anchor="center")
    tabela.column("Coluna Final", width=120, anchor="center")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Inserindo dados
    for t in tokens:
        tabela.insert(
            "",
            "end",
            values=(
                t.type,
                t.lexeme,
                t.line,
                t.col_start,
                t.col_end
            )
        )


root.mainloop()