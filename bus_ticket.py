"""

Bus Ticket Reservation System

==============================

- Full CRUD with auto-ID, keyboard shortcuts, right-click menu

- Live search across name / source / destination

- Sortable columns, export to CSV

- Analytics tab: fare filter, sorting, classification, pandas describe()

- Help tab with full usage guide

- Data persisted to bus_tickets.csv (same folder as script)

"""



import tkinter as tk

from tkinter import ttk, messagebox

import pandas as pd

import os

import random

import string

from datetime import datetime



# ================================================================

#  CONFIG

# ================================================================

DATA_FILE  = "bus_tickets.csv"

COLUMNS    = ["Ticket ID", "Passenger Name", "Source", "Destination", "Fare"]

LD_CUTOFF  = 500   # Fare > this => Long Distance



# ================================================================

#  COLOUR PALETTE  (dark navy theme)

# ================================================================

BG      = "#0B0D1A"

SURFACE = "#131626"

CARD    = "#1A1F35"

ACCENT  = "#4F8EF7"

PURPLE  = "#9B6EFF"

GREEN   = "#2ECC71"

AMBER   = "#F5A623"

RED     = "#E74C3C"

TEXT    = "#E0E6FF"

MUTED   = "#6B7A99"

BORDER  = "#252D4A"

SEL     = "#1E2B50"

HBG     = "#1A2040"



FONT_BODY  = ("Segoe UI", 10)

FONT_BOLD  = ("Segoe UI Semibold", 10)

FONT_HEAD  = ("Segoe UI Semibold", 12)

FONT_STAT  = ("Segoe UI Bold", 22)

FONT_SMALL = ("Segoe UI", 9)

FONT_MONO  = ("Consolas", 9)



# ================================================================

#  DATA LAYER

# ================================================================

def load_data():

    if os.path.exists(DATA_FILE):

        try:

            df = pd.read_csv(DATA_FILE, dtype={"Ticket ID": str})

            for c in COLUMNS:

                if c not in df.columns:

                    df[c] = ""

            return df[COLUMNS].copy()

        except Exception:

            pass

    return pd.DataFrame(columns=COLUMNS)





def save_data(df):

    df.to_csv(DATA_FILE, index=False)





def safe_float(v):

    try:

        return float(str(v).replace(",", "").strip())

    except Exception:

        return 0.0





def journey_type(fare):

    return "Long Distance" if safe_float(fare) > LD_CUTOFF else "Regular"





def gen_id(df):

    existing = set(df["Ticket ID"].tolist())

    for i in range(1, 9999):

        tid = f"TK-{i:03d}"

        if tid not in existing:

            return tid

    return "TK-" + "".join(random.choices(string.digits, k=4))



# ================================================================

#  CUSTOM PLACEHOLDER ENTRY

# ================================================================

class PlaceholderEntry(tk.Entry):

    def __init__(self, parent, placeholder="", **kw):

        self.ph = placeholder

        self._active = False

        super().__init__(parent, **kw)

        self._show_ph()

        self.bind("<FocusIn>",  self._on_focus_in)

        self.bind("<FocusOut>", self._on_focus_out)



    def _show_ph(self):

        self.config(state="normal")

        self.delete(0, tk.END)

        self.insert(0, self.ph)

        self.config(fg=MUTED)

        self._active = False



    def _on_focus_in(self, _=None):

        if not self._active:

            self.delete(0, tk.END)

            self.config(fg=TEXT)

            self._active = True



    def _on_focus_out(self, _=None):

        if not self.get().strip():

            self._show_ph()



    def get_value(self):

        return self.get().strip() if self._active else ""



    def set_value(self, val):

        self.config(state="normal")

        self.delete(0, tk.END)

        if val:

            self.insert(0, str(val))

            self.config(fg=TEXT)

            self._active = True

        else:

            self._show_ph()



    def clear(self):

        self._show_ph()





# ================================================================

#  HELPERS

# ================================================================

def make_btn(parent, text, color, cmd, small=False):

    f = FONT_SMALL if small else FONT_BOLD

    return tk.Button(

        parent, text=text, bg=color, fg="#0B0D1A",

        font=f, relief="flat", bd=0, cursor="hand2",

        activebackground=color, activeforeground="#0B0D1A",

        padx=10, pady=6 if small else 9, command=cmd

    )





def hsep(parent):

    return tk.Frame(parent, bg=BORDER, height=1)





# ================================================================

#  MAIN APPLICATION

# ================================================================

class App(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Bus Ticket Reservation System")

        self.geometry("1320x820")

        self.minsize(1060, 680)

        self.configure(bg=BG)

        self.df           = load_data()

        self._col_asc     = True

        self._status_var  = tk.StringVar(value="Ready  |  Click a row to load it into the form")

        self._clock_var   = tk.StringVar()

        self._rowcount    = tk.StringVar()

        self._setup_styles()

        self._build_ui()

        self._reload_table()

        self._tick()



    # ── styles ───────────────────────────────────────────────────

    def _setup_styles(self):

        s = ttk.Style(self)

        s.theme_use("clam")

        s.configure("T.Treeview",

            background=SURFACE, foreground=TEXT,

            fieldbackground=SURFACE, rowheight=36,

            bordercolor=BORDER, relief="flat", font=FONT_BODY)

        s.configure("T.Treeview.Heading",

            background=HBG, foreground=ACCENT,

            font=FONT_BOLD, relief="flat",

            bordercolor=BORDER, padding=(10, 7))

        s.map("T.Treeview",

            background=[("selected", SEL)],

            foreground=[("selected", TEXT)])

        s.map("T.Treeview.Heading",

            background=[("active", BORDER)])

        s.configure("Vertical.TScrollbar",

            background=BORDER, troughcolor=SURFACE,

            bordercolor=BORDER, arrowcolor=MUTED, relief="flat")

        s.configure("Horizontal.TScrollbar",

            background=BORDER, troughcolor=SURFACE,

            bordercolor=BORDER, arrowcolor=MUTED, relief="flat")

        s.configure("N.TNotebook",

            background=BG, tabmargins=[0, 4, 0, 0], bordercolor=BORDER)

        s.configure("N.TNotebook.Tab",

            background=CARD, foreground=MUTED,

            font=FONT_BOLD, padding=[22, 9], bordercolor=BORDER)

        s.map("N.TNotebook.Tab",

            background=[("selected", ACCENT)],

            foreground=[("selected", "#0B0D1A")])



    # ── top bar ──────────────────────────────────────────────────

    def _build_topbar(self):

        bar = tk.Frame(self, bg=CARD, height=60)

        bar.pack(fill=tk.X)

        bar.pack_propagate(False)

        tk.Label(bar, text="Bus", bg=CARD, fg=ACCENT,

                 font=("Segoe UI Semibold", 16)).pack(side=tk.LEFT, padx=(20, 2), pady=10)

        tk.Label(bar, text="Ticket Reservation System",

                 bg=CARD, fg=TEXT, font=("Segoe UI", 16)).pack(side=tk.LEFT, pady=10)

        tk.Label(bar, textvariable=self._clock_var,

                 bg=CARD, fg=MUTED, font=FONT_SMALL).pack(side=tk.RIGHT, padx=20, pady=10)

        hsep(self).pack(fill=tk.X)



    # ── stats bar ─────────────────────────────────────────────────

    def _build_statsbar(self):

        self._sf = tk.Frame(self, bg=BG)

        self._sf.pack(fill=tk.X, padx=16, pady=(12, 0))

        self._refresh_stats()



    def _refresh_stats(self):

        for w in self._sf.winfo_children():

            w.destroy()

        total = len(self.df)

        fares = self.df["Fare"].apply(safe_float) if total else pd.Series(dtype=float)

        ld    = int((fares > LD_CUTOFF).sum()) if total else 0

        reg   = total - ld

        avg   = fares.mean() if total else 0

        for title, val, color in [

            ("Total Tickets",  str(total),         ACCENT),

            ("Long Distance",  str(ld),             PURPLE),

            ("Regular",        str(reg),            GREEN),

            ("Average Fare",   f"INR {avg:.0f}",   AMBER),

        ]:

            c = tk.Frame(self._sf, bg=CARD,

                         highlightbackground=BORDER, highlightthickness=1)

            c.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

            tk.Label(c, text=title, bg=CARD, fg=MUTED,

                     font=FONT_SMALL).pack(anchor="w", padx=16, pady=(10, 0))

            tk.Label(c, text=val, bg=CARD, fg=color,

                     font=FONT_STAT).pack(anchor="w", padx=16, pady=(0, 10))



    # ── status bar ───────────────────────────────────────────────

    def _build_statusbar(self):

        bar = tk.Frame(self, bg=HBG, height=28)

        bar.pack(fill=tk.X, side=tk.BOTTOM)

        bar.pack_propagate(False)

        tk.Label(bar, textvariable=self._status_var,

                 bg=HBG, fg=MUTED, font=FONT_SMALL, anchor="w"

                 ).pack(side=tk.LEFT, padx=16, pady=4)

        tk.Label(bar, text=f"Journey classification: Fare > INR {LD_CUTOFF} = Long Distance",

                 bg=HBG, fg=MUTED, font=FONT_SMALL

                 ).pack(side=tk.RIGHT, padx=16, pady=4)



    def set_status(self, msg):

        self._status_var.set(msg)



    # ── main ui ──────────────────────────────────────────────────

    def _build_ui(self):

        self._build_topbar()

        self._build_statsbar()

        self._build_statusbar()    # pack BOTTOM before notebook

        nb = ttk.Notebook(self, style="N.TNotebook")

        nb.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        self._t1 = tk.Frame(nb, bg=BG)

        nb.add(self._t1, text="   Records   ")

        self._t2 = tk.Frame(nb, bg=BG)

        nb.add(self._t2, text="   Analytics   ")

        self._t3 = tk.Frame(nb, bg=BG)

        nb.add(self._t3, text="   Help   ")

        self._build_records_tab()

        self._build_analytics_tab()

        self._build_help_tab()



    # ============================================================

    #  TAB 1 - RECORDS

    # ============================================================

    def _build_records_tab(self):

        pane = tk.PanedWindow(self._t1, orient=tk.HORIZONTAL,

                              bg=BG, sashwidth=8, sashrelief="flat",

                              sashpad=2)

        pane.pack(fill=tk.BOTH, expand=True)



        # ── LEFT: form panel ────────────────────────────────────

        left = tk.Frame(pane, bg=SURFACE, width=315)

        pane.add(left, minsize=260)



        tk.Label(left, text="Ticket Details", bg=SURFACE, fg=TEXT,

                 font=FONT_HEAD).pack(anchor="w", padx=20, pady=(18, 4))

        tk.Label(left, text="Press F2 to Add  |  F3 to Update  |  Esc to Clear",

                 bg=SURFACE, fg=MUTED, font=FONT_SMALL

                 ).pack(anchor="w", padx=20, pady=(0, 8))

        hsep(left).pack(fill=tk.X, padx=20, pady=(0, 12))



        # Ticket ID row with Auto button

        self._entries = {}

        id_row = tk.Frame(left, bg=SURFACE)

        id_row.pack(fill=tk.X, padx=20)

        tk.Label(id_row, text="Ticket ID *", bg=SURFACE, fg=MUTED,

                 font=FONT_SMALL).pack(anchor="w")

        id_inner = tk.Frame(id_row, bg=SURFACE)

        id_inner.pack(fill=tk.X, pady=(3, 0))

        e_id = PlaceholderEntry(id_inner, placeholder="e.g. TK-001",

                                bg=CARD, fg=TEXT, insertbackground=TEXT,

                                relief="flat", font=FONT_BODY, bd=0)

        e_id.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        make_btn(id_inner, "Auto", BORDER, self._auto_id, small=True

                 ).pack(side=tk.LEFT, padx=(6, 0))

        self._entries["Ticket ID"] = e_id



        # Remaining fields

        for lbl, key, ph in [

            ("Passenger Name *", "Passenger Name", "Full name"),

            ("Source *",          "Source",          "Departure city"),

            ("Destination *",     "Destination",     "Arrival city"),

            ("Fare (INR) *",      "Fare",            "e.g. 350"),

        ]:

            f = tk.Frame(left, bg=SURFACE)

            f.pack(fill=tk.X, padx=20, pady=(10, 0))

            tk.Label(f, text=lbl, bg=SURFACE, fg=MUTED,

                     font=FONT_SMALL).pack(anchor="w")

            e = PlaceholderEntry(f, placeholder=ph,

                                 bg=CARD, fg=TEXT, insertbackground=TEXT,

                                 relief="flat", font=FONT_BODY, bd=0)

            e.pack(fill=tk.X, ipady=8, pady=(3, 0))

            self._entries[key] = e



        self._entries["Fare"].bind("<Return>", lambda _: self._add())



        hsep(left).pack(fill=tk.X, padx=20, pady=(18, 12))



        # CRUD buttons

        for text, color, cmd in [

            ("+ Add Ticket",   GREEN,  self._add),

            ("Save Changes",   ACCENT, self._update),

            ("Delete Ticket",  RED,    self._delete),

            ("Clear / New",    BORDER, self._clear),

        ]:

            make_btn(left, text, color, cmd).pack(fill=tk.X, padx=20, pady=3)



        hsep(left).pack(fill=tk.X, padx=20, pady=(14, 10))



        # Search

        tk.Label(left, text="Search  (name / source / destination)",

                 bg=SURFACE, fg=MUTED, font=FONT_SMALL

                 ).pack(anchor="w", padx=20)

        self._sv = tk.StringVar()

        self._sv.trace_add("write", lambda *_: self._search())

        tk.Entry(left, textvariable=self._sv,

                 bg=CARD, fg=TEXT, insertbackground=TEXT,

                 relief="flat", font=FONT_BODY, bd=0

                 ).pack(fill=tk.X, padx=20, pady=(4, 0), ipady=8)

        make_btn(left, "Clear Search", BORDER,

                 lambda: self._sv.set(""), small=True

                 ).pack(anchor="e", padx=20, pady=4)



        hsep(left).pack(fill=tk.X, padx=20, pady=(8, 8))

        make_btn(left, "Export to CSV", AMBER, self._export, small=True

                 ).pack(fill=tk.X, padx=20, pady=(0, 14))



        # ── RIGHT: table ─────────────────────────────────────────

        right = tk.Frame(pane, bg=BG)

        pane.add(right, minsize=620)



        # Toolbar above table

        tb = tk.Frame(right, bg=BG)

        tb.pack(fill=tk.X, pady=(0, 8))

        make_btn(tb, "Fare Low -> High", GREEN,  lambda: self._sort_table(True),  small=True).pack(side=tk.LEFT, padx=(0, 6))

        make_btn(tb, "Fare High -> Low", AMBER,  lambda: self._sort_table(False), small=True).pack(side=tk.LEFT, padx=(0, 6))

        make_btn(tb, "Refresh",          ACCENT, self._reload_table,              small=True).pack(side=tk.LEFT)

        tk.Label(tb, textvariable=self._rowcount,

                 bg=BG, fg=MUTED, font=FONT_SMALL).pack(side=tk.RIGHT)



        # Treeview

        cols = ["#", "Ticket ID", "Passenger Name", "Source", "Destination", "Fare", "Journey Type"]

        tf = tk.Frame(right, bg=SURFACE,

                      highlightbackground=BORDER, highlightthickness=1)

        tf.pack(fill=tk.BOTH, expand=True)



        self._tree = ttk.Treeview(tf, columns=cols, show="headings",

                                  style="T.Treeview", selectmode="browse")

        for col, w in zip(cols, [40, 95, 175, 130, 140, 90, 135]):

            self._tree.heading(col, text=col,

                               command=lambda c=col: self._col_sort(c))

            self._tree.column(col, width=w, minwidth=36,

                              anchor="center" if col == "#" else "w")



        vsb = ttk.Scrollbar(tf, orient="vertical",

                            command=self._tree.yview)

        hsb = ttk.Scrollbar(tf, orient="horizontal",

                            command=self._tree.xview)

        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self._tree.pack(fill=tk.BOTH, expand=True)



        # Row colour tags

        self._tree.tag_configure("ld",   background="#1B1040", foreground=PURPLE)

        self._tree.tag_configure("ld2",  background="#160D38", foreground=PURPLE)

        self._tree.tag_configure("reg",  background=SURFACE,   foreground=TEXT)

        self._tree.tag_configure("reg2", background="#111524", foreground=TEXT)



        # Right-click context menu

        self._ctx = tk.Menu(self, tearoff=0, bg=CARD, fg=TEXT,

                            activebackground=ACCENT, activeforeground="#0B0D1A",

                            font=FONT_BODY, relief="flat")

        self._ctx.add_command(label="Edit Selected",  command=self._update)

        self._ctx.add_command(label="Delete Selected", command=self._delete)

        self._ctx.add_separator()

        self._ctx.add_command(label="Copy Ticket ID", command=self._copy_id)

        self._ctx.add_command(label="Clear Form",     command=self._clear)



        self._tree.bind("<Button-3>",           self._show_ctx)

        self._tree.bind("<<TreeviewSelect>>",   self._on_select)



        # Global shortcuts

        self.bind("<F2>",     lambda _: self._add())

        self.bind("<F3>",     lambda _: self._update())

        self.bind("<Escape>", lambda _: self._clear())



    # ============================================================

    #  TAB 2 - ANALYTICS

    # ============================================================

    def _build_analytics_tab(self):

        t = self._t2



        # Filter card

        fc = tk.Frame(t, bg=CARD, highlightbackground=BORDER, highlightthickness=1)

        fc.pack(fill=tk.X, pady=(0, 12))

        inner = tk.Frame(fc, bg=CARD)

        inner.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(inner, text="Show passengers paying more than:",

                 bg=CARD, fg=TEXT, font=FONT_BOLD).pack(side=tk.LEFT)

        self._fare_var = tk.StringVar(value="0")

        tk.Entry(inner, textvariable=self._fare_var,

                 bg=SURFACE, fg=TEXT, insertbackground=TEXT,

                 relief="flat", font=FONT_BODY, bd=0, width=10

                 ).pack(side=tk.LEFT, padx=10, ipady=7)

        tk.Label(inner, text="INR", bg=CARD, fg=AMBER,

                 font=FONT_BOLD).pack(side=tk.LEFT)

        make_btn(inner, "Apply Filter", ACCENT, self._fare_filter, small=True

                 ).pack(side=tk.LEFT, padx=12)

        self._fcnt_var = tk.StringVar()

        tk.Label(inner, textvariable=self._fcnt_var, bg=CARD, fg=GREEN,

                 font=FONT_BODY).pack(side=tk.LEFT)



        # Action buttons row

        ab = tk.Frame(t, bg=BG)

        ab.pack(fill=tk.X, pady=(0, 8))

        for text, color, cmd in [

            ("Sort Asc",           GREEN,  lambda: self._ana_sort(True)),

            ("Sort Desc",          AMBER,  lambda: self._ana_sort(False)),

            ("Classify All",       PURPLE, self._classify_all),

            ("Pandas Statistics",  ACCENT, self._pandas_summary),

            ("Reset",              BORDER, self._ana_reset),

        ]:

            make_btn(ab, text, color, cmd, small=True).pack(side=tk.LEFT, padx=(0, 6))



        # Analytics treeview

        af = tk.Frame(t, bg=SURFACE,

                      highlightbackground=BORDER, highlightthickness=1)

        af.pack(fill=tk.BOTH, expand=True)

        acols = ["#", "Ticket ID", "Passenger Name", "Source", "Destination", "Fare", "Journey Type"]

        self._atree = ttk.Treeview(af, columns=acols, show="headings",

                                   style="T.Treeview", selectmode="none")

        for col, w in zip(acols, [40, 95, 185, 130, 140, 90, 135]):

            self._atree.heading(col, text=col)

            self._atree.column(col, width=w, minwidth=36,

                               anchor="center" if col == "#" else "w")

        avsb = ttk.Scrollbar(af, orient="vertical",
                     command=self._atree.yview,
                     style="Vertical.TScrollbar")

        self._atree.configure(yscrollcommand=avsb.set)
        


        avsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._atree.pack(fill=tk.BOTH, expand=True)

        self._atree.tag_configure("ld",   background="#1B1040", foreground=PURPLE)

        self._atree.tag_configure("ld2",  background="#160D38", foreground=PURPLE)

        self._atree.tag_configure("reg",  background=SURFACE,   foreground=GREEN)

        self._atree.tag_configure("reg2", background="#0D1A10", foreground=GREEN)



        # Pandas output panel

        sf = tk.Frame(t, bg=HBG, highlightbackground=BORDER, highlightthickness=1)

        sf.pack(fill=tk.X, pady=(8, 0))

        tk.Label(sf, text="Pandas Output:", bg=HBG, fg=ACCENT,

                 font=FONT_SMALL).pack(anchor="w", padx=12, pady=(6, 0))

        self._stxt = tk.Text(sf, bg=HBG, fg=TEXT, height=7,

                             font=FONT_MONO, relief="flat",

                             insertbackground=TEXT, bd=0, state="disabled")

        self._stxt.pack(fill=tk.X, padx=12, pady=(2, 8))



    # ============================================================

    #  TAB 3 - HELP

    # ============================================================

    def _build_help_tab(self):

        t = self._t3

        cv = tk.Canvas(t, bg=BG, highlightthickness=0)

        sb = ttk.Scrollbar(t, orient="vertical", command=cv.yview)

        cv.configure(yscrollcommand=sb.set)

        sb.pack(side=tk.RIGHT, fill=tk.Y)

        cv.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(cv, bg=BG)

        win = cv.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda _: cv.configure(scrollregion=cv.bbox("all")))

        cv.bind("<Configure>", lambda e: cv.itemconfig(win, width=e.width))



        def sec(title, rows):

            tk.Label(inner, text=title, bg=BG, fg=ACCENT,

                     font=FONT_HEAD, anchor="w"

                     ).pack(fill=tk.X, padx=28, pady=(22, 6))

            hsep(inner).pack(fill=tk.X, padx=28, pady=(0, 8))

            for k, v in rows:

                r = tk.Frame(inner, bg=BG)

                r.pack(fill=tk.X, padx=28, pady=3)

                tk.Label(r, text=k, bg=BG, fg=TEXT,

                         font=FONT_BOLD, width=24, anchor="w"

                         ).pack(side=tk.LEFT)

                tk.Label(r, text=v, bg=BG, fg=MUTED,

                         font=FONT_BODY, anchor="w", justify="left",

                         wraplength=720

                         ).pack(side=tk.LEFT, fill=tk.X, expand=True)



        sec("Quick Start - Records Tab", [

            ("Add a ticket",       "Fill the form on the left, then click '+ Add Ticket' (or press F2)."),

            ("Auto Ticket ID",     "Click the 'Auto' button to automatically generate the next Ticket ID."),

            ("Edit a ticket",      "Click any row in the table - the form fills automatically. Edit and press 'Save Changes' (F3)."),

            ("Delete a ticket",    "Select a row and click 'Delete Ticket', or right-click > Delete."),

            ("Search",             "Type in the Search box to instantly filter by name, source, or destination."),

            ("Sort by column",     "Click any column header to sort ascending/descending. Or use the toolbar buttons to sort by fare."),

            ("Export to CSV",      "Click 'Export to CSV' to save a timestamped snapshot of current data."),

        ])

        sec("Analytics Tab", [

            ("Filter by fare",     "Enter a fare amount and click 'Apply Filter' to see only passengers paying above that amount."),

            ("Sort Asc / Desc",    "Sort all records by fare in ascending or descending order."),

            ("Classify All",       "View all records with journey type highlighted. Purple = Long Distance, Green = Regular."),

            ("Pandas Statistics",  "Shows pandas describe() statistics: count, mean, min, max, std for fare column."),

            ("Classification rule",f"Fare > INR {LD_CUTOFF} => Long Distance.   Fare <= INR {LD_CUTOFF} => Regular."),

        ])

        sec("Keyboard Shortcuts", [

            ("F2",           "Add a new ticket"),

            ("F3",           "Save / Update current ticket"),

            ("Escape",       "Clear the form"),

            ("Enter",        "In the Fare field: adds the ticket"),

            ("Right-click",  "Context menu on any row: Edit / Delete / Copy ID"),

        ])

        sec("Data Storage", [

            ("File",        "All data is saved to 'bus_tickets.csv' in the same folder as the script."),

            ("Auto-save",   "Every add, update, or delete immediately writes to disk."),

            ("Pandas",      "The app uses pandas DataFrames internally for all filtering, sorting, and statistics."),

        ])



    # ============================================================

    #  CRUD OPERATIONS

    # ============================================================

    def _get_form(self):

        return {k: e.get_value() for k, e in self._entries.items()}



    def _add(self):

        v = self._get_form()

        if not all(v.values()):

            messagebox.showwarning("Missing Fields",

                "All fields are required.\n\nPlease fill in every field before adding.",

                parent=self)

            return

        try:

            fare = float(v["Fare"])

            if fare <= 0:

                raise ValueError

        except ValueError:

            messagebox.showerror("Invalid Fare",

                "Fare must be a positive number (e.g. 450).",

                parent=self)

            return

        if v["Ticket ID"] in self.df["Ticket ID"].values:

            messagebox.showerror("Duplicate Ticket ID",

                f"Ticket ID '{v['Ticket ID']}' already exists.\n\n"

                "Use the 'Auto' button to generate a unique ID.",

                parent=self)

            return

        row = pd.DataFrame([{

            "Ticket ID":      v["Ticket ID"],

            "Passenger Name": v["Passenger Name"],

            "Source":         v["Source"],

            "Destination":    v["Destination"],

            "Fare":           fare,

        }])

        self.df = pd.concat([self.df, row], ignore_index=True)

        save_data(self.df)

        self._reload_table()

        self._clear()

        self.set_status(f"Added: {v['Ticket ID']}  |  {v['Passenger Name']}  |  {v['Source']} -> {v['Destination']}  |  INR {fare:,.0f}  |  {journey_type(fare)}")



    def _update(self):

        v = self._get_form()

        if not v["Ticket ID"]:

            messagebox.showwarning("No Ticket ID",

                "Click a row in the table to select it, then edit the fields and press 'Save Changes'.",

                parent=self)

            return

        if not all(v.values()):

            messagebox.showwarning("Missing Fields",

                "Fill all fields before updating.", parent=self)

            return

        try:

            fare = float(v["Fare"])

            if fare <= 0:

                raise ValueError

        except ValueError:

            messagebox.showerror("Invalid Fare",

                "Fare must be a positive number.", parent=self)

            return

        mask = self.df["Ticket ID"] == v["Ticket ID"]

        if not mask.any():

            messagebox.showerror("Not Found",

                f"Ticket ID '{v['Ticket ID']}' was not found in records.", parent=self)

            return

        self.df.loc[mask, "Passenger Name"] = v["Passenger Name"]

        self.df.loc[mask, "Source"]          = v["Source"]

        self.df.loc[mask, "Destination"]     = v["Destination"]

        self.df.loc[mask, "Fare"]            = fare

        save_data(self.df)

        self._reload_table()

        self._clear()

        self.set_status(f"Updated: {v['Ticket ID']}  |  {v['Passenger Name']}  |  INR {fare:,.0f}")



    def _delete(self):

        v   = self._get_form()

        tid = v.get("Ticket ID", "")

        if not tid:

            sel = self._tree.selection()

            if sel:

                tid = str(self._tree.item(sel[0])["values"][1])

        if not tid:

            messagebox.showwarning("No Selection",

                "Click a row in the table to select it first.", parent=self)

            return

        if not messagebox.askyesno("Confirm Delete",

            f"Permanently delete ticket '{tid}'?\n\nThis action cannot be undone.",

            parent=self):

            return

        self.df = self.df[self.df["Ticket ID"] != tid].reset_index(drop=True)

        save_data(self.df)

        self._reload_table()

        self._clear()

        self.set_status(f"Deleted ticket: {tid}")



    def _clear(self):

        for e in self._entries.values():

            e.clear()

        if self._tree.selection():

            self._tree.selection_remove(self._tree.selection())

        self.set_status("Form cleared  |  Ready to add a new ticket")



    def _auto_id(self):

        self._entries["Ticket ID"].set_value(gen_id(self.df))

        self.set_status("Auto-generated Ticket ID. Fill remaining fields and click '+ Add Ticket'.")



    def _copy_id(self):

        sel = self._tree.selection()

        if sel:

            tid = str(self._tree.item(sel[0])["values"][1])

            self.clipboard_clear()

            self.clipboard_append(tid)

            self.set_status(f"Copied '{tid}' to clipboard.")



    def _export(self):

        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")

        out = f"bus_tickets_export_{ts}.csv"

        self.df.to_csv(out, index=False)

        messagebox.showinfo("Export Successful",

            f"Data exported to:\n{os.path.abspath(out)}", parent=self)

        self.set_status(f"Exported {len(self.df)} records -> {out}")



    # ============================================================

    #  TABLE HELPERS

    # ============================================================

    def _reload_table(self, df=None):

        self._refresh_stats()

        data = df if df is not None else self.df

        self._fill_tree(self._tree, data)

        self._rowcount.set(f"{len(data)} record(s)")



    def _fill_tree(self, tree, df):

        tree.delete(*tree.get_children())

        for i, (_, r) in enumerate(df.iterrows()):

            fare  = safe_float(r["Fare"])

            jtype = journey_type(fare)

            is_ld = fare > LD_CUTOFF

            even  = i % 2 == 0

            tag   = ("ld" if even else "ld2") if is_ld else ("reg" if even else "reg2")

            tree.insert("", tk.END, values=(

                i + 1,

                r["Ticket ID"],

                r["Passenger Name"],

                r["Source"],

                r["Destination"],

                f"{fare:,.0f}",

                jtype,

            ), tags=(tag,))



    def _on_select(self, _):

        sel = self._tree.selection()

        if not sel:

            return

        vals = self._tree.item(sel[0])["values"]

        # vals: (#, Ticket ID, Name, Source, Dest, Fare, JType)

        keys = ["Ticket ID", "Passenger Name", "Source", "Destination", "Fare"]

        for key, val in zip(keys, vals[1:6]):

            self._entries[key].set_value(str(val).replace(",", "").strip())

        self.set_status(

            f"Selected: {vals[2]}  |  {vals[1]}  |  {vals[3]} -> {vals[4]}"

            f"  |  INR {vals[5]}  |  {vals[6]}"

        )



    def _show_ctx(self, event):

        row = self._tree.identify_row(event.y)

        if row:

            self._tree.selection_set(row)

            try:

                self._ctx.post(event.x_root, event.y_root)

            finally:

                self._ctx.grab_release()



    def _search(self):

        q = self._sv.get().strip().lower()

        if not q:

            self._reload_table()

            return

        mask = (

            self.df["Passenger Name"].str.lower().str.contains(q, na=False) |

            self.df["Source"].str.lower().str.contains(q, na=False) |

            self.df["Destination"].str.lower().str.contains(q, na=False)

        )

        self._reload_table(self.df[mask])



    def _sort_table(self, asc):

        sdf = self.df.copy()

        sdf["Fare"] = sdf["Fare"].apply(safe_float)

        sdf = sdf.sort_values("Fare", ascending=asc)

        self._fill_tree(self._tree, sdf)

        self.set_status(f"Sorted by Fare ({'ascending' if asc else 'descending'}).")



    def _col_sort(self, col):

        items = list(self._tree.get_children())

        num_cols = {"#", "Fare"}

        if col in num_cols:

            key = lambda k: safe_float(str(self._tree.set(k, col)).replace(",", ""))

        else:

            key = lambda k: str(self._tree.set(k, col)).lower()

        items.sort(key=key, reverse=not self._col_asc)

        for idx, k in enumerate(items):

            self._tree.move(k, "", idx)

        self._col_asc = not self._col_asc



    # ============================================================

    #  ANALYTICS

    # ============================================================

    def _fare_filter(self):

        try:

            thr = float(self._fare_var.get())

        except ValueError:

            messagebox.showerror("Invalid", "Please enter a numeric fare amount.", parent=self)

            return

        df = self.df.copy()

        df["Fare"] = df["Fare"].apply(safe_float)

        res = df[df["Fare"] > thr].copy()

        res["Journey Type"] = res["Fare"].apply(journey_type)

        count = len(res)

        self._fcnt_var.set(f"  {count} passenger(s) found")

        self._fill_atree(res)

        if count:

            txt = f"Passengers paying MORE than INR {thr:.0f}  ({count} found)\n"

            txt += "=" * 54 + "\n"

            txt += res[["Passenger Name", "Source", "Destination", "Fare", "Journey Type"]

                       ].to_string(index=False)

        else:

            txt = f"No passengers found with fare above INR {thr:.0f}."

        self._set_summary(txt)

        self.set_status(f"Filter applied: {count} passenger(s) paying above INR {thr:.0f}")



    def _ana_sort(self, asc):

        df = self.df.copy()

        df["Fare"] = df["Fare"].apply(safe_float)

        df["Journey Type"] = df["Fare"].apply(journey_type)

        df = df.sort_values("Fare", ascending=asc)

        self._fill_atree(df)

        txt = f"All records sorted by Fare ({'ascending' if asc else 'descending'})\n"

        txt += "=" * 50 + "\n"

        txt += df[["Ticket ID", "Passenger Name", "Fare", "Journey Type"]

                  ].to_string(index=False)

        self._set_summary(txt)

        self.set_status(f"Analytics: sorted by fare ({'asc' if asc else 'desc'}).")



    def _classify_all(self):

        df = self.df.copy()

        df["Fare"] = df["Fare"].apply(safe_float)

        df["Journey Type"] = df["Fare"].apply(journey_type)

        self._fill_atree(df)

        grp = df.groupby("Journey Type")["Fare"].agg(["count", "mean", "min", "max"])

        grp.columns = ["Count", "Mean Fare", "Min Fare", "Max Fare"]

        txt = f"Journey Classification  (threshold: INR {LD_CUTOFF})\n"

        txt += "=" * 50 + "\n"

        txt += grp.round(2).to_string()

        txt += f"\n\n  Long Distance  = Fare > INR {LD_CUTOFF}  (shown in purple)\n"

        txt +=  "  Regular        = Fare <= INR {0}  (shown in green)\n".format(LD_CUTOFF)

        self._set_summary(txt)

        self.set_status("Classified all records by journey type.")



    def _pandas_summary(self):

        df = self.df.copy()

        df["Fare"] = df["Fare"].apply(safe_float)

        desc = df["Fare"].describe().round(2)

        txt  = "Pandas Fare Statistics - DataFrame.describe()\n"

        txt += "=" * 44 + "\n"

        txt += desc.to_string()

        txt += f"\n\nLong Distance (Fare > INR {LD_CUTOFF}): {int((df['Fare'] > LD_CUTOFF).sum())} passengers"

        txt += f"\nRegular (Fare <= INR {LD_CUTOFF}):       {int((df['Fare'] <= LD_CUTOFF).sum())} passengers"

        self._set_summary(txt)

        self._fill_atree(df)

        self.set_status("Pandas describe() statistics displayed below.")



    def _ana_reset(self):

        self._fill_atree(self.df)

        self._fcnt_var.set("")

        self._set_summary("")

        self.set_status("Analytics view reset.")



    def _fill_atree(self, df):

        self._atree.delete(*self._atree.get_children())

        for i, (_, r) in enumerate(df.iterrows()):

            fare  = safe_float(r.get("Fare", 0))

            jtype = r.get("Journey Type", journey_type(fare))

            is_ld = fare > LD_CUTOFF

            even  = i % 2 == 0

            tag   = ("ld" if even else "ld2") if is_ld else ("reg" if even else "reg2")

            self._atree.insert("", tk.END, values=(

                i + 1,

                r.get("Ticket ID", ""),

                r.get("Passenger Name", ""),

                r.get("Source", ""),

                r.get("Destination", ""),

                f"{fare:,.0f}",

                jtype,

            ), tags=(tag,))



    def _set_summary(self, text):

        self._stxt.config(state="normal")

        self._stxt.delete("1.0", tk.END)

        self._stxt.insert("1.0", text)

        self._stxt.config(state="disabled")



    # ── clock ─────────────────────────────────────────────────

    def _tick(self):

        self._clock_var.set(datetime.now().strftime("%d %b %Y  %H:%M:%S"))

        self.after(1000, self._tick)





# ================================================================

#  ENTRY POINT

# ================================================================

SAMPLE = [

    ("TK-001", "Aarav Sharma",   "Delhi",     "Mumbai",    850),

    ("TK-002", "Priya Nair",     "Chennai",   "Bangalore", 280),

    ("TK-003", "Rohit Verma",    "Kolkata",   "Patna",     320),

    ("TK-004", "Sneha Joshi",    "Pune",      "Hyderabad", 620),

    ("TK-005", "Vikram Rao",     "Ahmedabad", "Jaipur",    450),

    ("TK-006", "Ananya Mishra",  "Lucknow",   "Delhi",     390),

    ("TK-007", "Karan Mehta",    "Bengaluru", "Goa",       750),

    ("TK-008", "Deepika Singh",  "Bhopal",    "Indore",    150),

    ("TK-009", "Arjun Pillai",   "Kochi",     "Calicut",   210),

    ("TK-010", "Meera Reddy",    "Vizag",     "Chennai",   530),

]



if __name__ == "__main__":

    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) < 10:

        pd.DataFrame(SAMPLE, columns=COLUMNS).to_csv(DATA_FILE, index=False)

    app = App()

    app.mainloop()
