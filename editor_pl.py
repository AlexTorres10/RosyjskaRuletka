import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from itertools import permutations

class EditorPerguntas:
    def __init__(self, root):
        self.root = root
        self.root.title("Question Editor Rosyjska Ruletka")
        self.root.geometry("900x600")
        self.unsaved = False

        # Mapping for round display to numeric
        self.round_map = {
            "Round 1": "1",
            "Round 2": "2",
            "Round 3": "3",
            "Round 4": "4",
            "Final Round": "5"
        }

        # Load or initialize DataFrame
        self.df = self.load_data()
        self.visible_indices = []
        self.current_index = None

        # Build interface
        self.create_menu()
        self.create_widgets()
        self.update_listbox()

        # Handle close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        try:
            df = pd.read_csv("main.csv", sep=';', encoding='utf-8')
            df = df[['question','right','alt1','alt2','alt3','alt4','shuffle','round']]
        except Exception:
            df = pd.DataFrame(columns=['question','right','alt1','alt2','alt3','alt4','shuffle','round'])
        return df

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        menu_bar.add_command(label="New Base", command=self.new_base)
        menu_bar.add_command(label="Open Base", command=self.open_base)
        menu_bar.add_command(label="Save Base", command=self.save_data)
        self.root.config(menu=menu_bar)

    def new_base(self):
        if self.unsaved and messagebox.askyesno("Unsaved Changes", "Save current changes before creating a new base?" ):
            self.save_data()
        self.df = pd.DataFrame(columns=['question','right','alt1','alt2','alt3','alt4','shuffle','round'])
        self.visible_indices = []
        self.current_index = None
        self.unsaved = False
        self.update_listbox()

    def create_widgets(self):
        # Left panel
        frame_left = tk.Frame(self.root)
        tk.Label(frame_left, text="Search:").pack(anchor='w', pady=2)
        self.search_var = tk.StringVar()
        tk.Entry(frame_left, textvariable=self.search_var, width=30).pack(anchor='w')
        self.search_var.trace_add('write', lambda *args: self.update_listbox())
        self.listbox = tk.Listbox(frame_left, height=30, width=40)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Right panel
        frame_right = tk.Frame(self.root)
        cols = ['question','right','alt1','alt2','alt3','alt4']
        self.entries = {}
        for i, c in enumerate(cols):
            tk.Label(frame_right, text=c.capitalize()+":").grid(row=i, column=0, sticky='w', pady=2)
            e = tk.Entry(frame_right, width=90)
            e.grid(row=i, column=1, pady=2)
            self.entries[c] = e

        # Round combobox
        idx = len(cols)
        tk.Label(frame_right, text="Round:").grid(row=idx, column=0, sticky='w', pady=2)
        self.round_var = tk.StringVar()
        self.combo_round = ttk.Combobox(
            frame_right, textvariable=self.round_var,
            values=list(self.round_map.keys()), state='readonly', width=58
        )
        self.combo_round.grid(row=idx, column=1, pady=2)
        self.combo_round.bind('<<ComboboxSelected>>', self.atualizar_opcoes_ordem)
        self.combo_round.current(0)

        # Shuffle combobox
        tk.Label(frame_right, text="Shuffle:").grid(row=idx+1, column=0, sticky='w', pady=2)
        self.shuffle_var = tk.StringVar()
        self.combo_shuffle = ttk.Combobox(
            frame_right, textvariable=self.shuffle_var,
            state='readonly', width=58
        )
        self.combo_shuffle.grid(row=idx+1, column=1, pady=2)
        self.atualizar_opcoes_ordem()

        # Buttons
        tk.Button(frame_right, text="Add Question", command=self.add_question).grid(row=idx+2, column=0, pady=10)
        tk.Button(frame_right, text="Replace Question", command=self.replace_question).grid(row=idx+2, column=1, pady=10)
        frame_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def atualizar_opcoes_ordem(self, event=None):
        disp = self.round_var.get()
        rd = int(self.round_map.get(disp, "1"))
        count = rd+1 if rd<4 else 5
        letters = [chr(ord('A')+i) for i in range(count)]
        perms = [''.join(p) for p in permutations(letters)]
        opts = ["Any order"] + perms
        self.combo_shuffle['values'] = opts
        cur = self.shuffle_var.get()
        self.combo_shuffle.set(cur if cur in opts else "Any order")

    def update_listbox(self):
        q = self.search_var.get().lower()
        df_f = self.df[self.df['question'].str.lower().str.contains(q, na=False)]
        self.visible_indices = df_f.index.tolist()
        self.listbox.delete(0, tk.END)
        for i in self.visible_indices:
            self.listbox.insert(tk.END, self.df.at[i,'question'])

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        # Determine actual DataFrame index
        idx_df = self.visible_indices[sel[0]]
        # Clear filter to show full list
        self.search_var.set('')
        # After clearing, update_listbox runs and fills full list
        # Now highlight the same question
        full_indices = self.visible_indices
        new_pos = full_indices.index(idx_df)
        self.listbox.selection_set(new_pos)
        self.listbox.see(new_pos)
        self.current_index = idx_df

        row = self.df.loc[idx_df]
        # Populate fields
        for c in ['question','right','alt1','alt2','alt3','alt4']:
            e = self.entries[c]
            e.delete(0, tk.END)
            e.insert(0, row.get(c, ''))
        # Set round combobox
        disp = next((k for k,v in self.round_map.items() if v==str(row.get('round'))), 'Round 1')
        self.round_var.set(disp)

        # Update shuffle options and set value
        self.atualizar_opcoes_ordem()
        raw = str(row.get('shuffle','')).strip()
        if raw in ['N','-','']:
            self.shuffle_var.set('Any order')
        else:
            try:
                letters = ''.join(chr(ord('A')+int(d)-1) for d in raw)
                self.shuffle_var.set(letters)
            except:
                self.shuffle_var.set('Any order')

    def validate_round(self):
        disp = self.round_var.get()
        if disp not in self.round_map:
            messagebox.showerror("Invalid Round", "Select a round from dropdown.")
            return None
        rd = int(self.round_map[disp])
        count_opts = sum(1 for k in ['right','alt1','alt2','alt3','alt4']
                         if self.entries[k].get().strip() and self.entries[k].get().strip()!="-")
        req = rd+1 if rd<4 else 5
        if count_opts!=req:
            messagebox.showerror("Invalid Alternatives",
                                 f"Round {rd} requires {req} options; got {count_opts}.")
            return None
        return rd

    def add_question(self):
        rd = self.validate_round()
        if rd is None: return
        data = {c:self.entries[c].get().strip() for c in ['question','right','alt1','alt2','alt3','alt4']}
        sd = self.shuffle_var.get()
        data['shuffle'] = 'N' if sd=='Any order' else ''.join(str(ord(ch)-ord('A')+1) for ch in sd)
        data['round'] = rd
        self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)
        self.unsaved=True
        self.update_listbox()
        messagebox.showinfo("Added","Question added. Don't forget to save.")

    def replace_question(self):
        if self.current_index is None:
            messagebox.showwarning("No selection","Select a question to replace.")
            return
        rd = self.validate_round()
        if rd is None: return
        for c in ['question','right','alt1','alt2','alt3','alt4']:
            self.df.at[self.current_index,c]=self.entries[c].get().strip()
        sd = self.shuffle_var.get()
        self.df.at[self.current_index,'shuffle']='N' if sd=='Any order' else ''.join(str(ord(ch)-ord('A')+1) for ch in sd)
        self.df.at[self.current_index,'round']=rd
        self.unsaved=True
        self.update_listbox()
        messagebox.showinfo("Replaced","Question updated. Don't forget to save.")

    def save_data(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if path:
            self.df.to_csv(path,sep=';',index=False,encoding='utf-8')
            self.unsaved=False
            messagebox.showinfo("Saved","Database saved successfully.")

    def open_base(self):
        path = filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if path:
            try:
                df = pd.read_csv(path,sep=';',encoding='utf-8')
                self.df = df[['question','right','alt1','alt2','alt3','alt4','shuffle','round']]
                self.unsaved=False
                self.update_listbox()
            except Exception as e:
                messagebox.showerror("Error",f"Failed to open file:\n{e}")

    def on_closing(self):
        if self.unsaved:
            resp=messagebox.askyesnocancel("Unsaved Changes","You have unsaved changes. Save before exit?")
            if resp is None: return
            if resp: self.save_data()
        self.root.destroy()

if __name__=='__main__':
    root=tk.Tk()
    app=EditorPerguntas(root)
    root.mainloop()
