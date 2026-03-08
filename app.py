from __future__ import annotations

from datetime import date
from tkinter import END, StringVar, Tk, messagebox, ttk

from db import BookkeepingDB


class BookkeepingApp:
    def __init__(self, root: Tk, db: BookkeepingDB) -> None:
        self.root = root
        self.db = db
        self.root.title("Bokföring för förening")
        self.root.geometry("980x660")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.overview_tab = ttk.Frame(self.notebook)
        self.accounts_tab = ttk.Frame(self.notebook)
        self.vouchers_tab = ttk.Frame(self.notebook)
        self.ledger_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.overview_tab, text="Översikt")
        self.notebook.add(self.accounts_tab, text="Kontoplan")
        self.notebook.add(self.vouchers_tab, text="Verifikation")
        self.notebook.add(self.ledger_tab, text="Huvudbok")

        self._build_overview_tab()
        self._build_accounts_tab()
        self._build_vouchers_tab()
        self._build_ledger_tab()
        self.refresh_all()

    def _build_overview_tab(self) -> None:
        self.summary_labels: dict[str, ttk.Label] = {}
        grid = ttk.Frame(self.overview_tab)
        grid.pack(fill="x", padx=12, pady=12)
        for idx, key in enumerate(("assets", "liabilities", "income", "expense")):
            frame = ttk.LabelFrame(grid, text=key.capitalize())
            frame.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=8, pady=8)
            label = ttk.Label(frame, text="0.00", font=("Arial", 14, "bold"))
            label.pack(padx=14, pady=12)
            self.summary_labels[key] = label

        self.recent_tree = ttk.Treeview(
            self.overview_tab,
            columns=("date", "desc", "debit", "credit"),
            show="headings",
        )
        for col, title in [
            ("date", "Datum"),
            ("desc", "Beskrivning"),
            ("debit", "Debet"),
            ("credit", "Kredit"),
        ]:
            self.recent_tree.heading(col, text=title)
            self.recent_tree.column(col, width=220)
        self.recent_tree.pack(fill="both", expand=True, padx=12, pady=12)

    def _build_accounts_tab(self) -> None:
        form = ttk.Frame(self.accounts_tab)
        form.pack(fill="x", padx=12, pady=12)

        self.account_number = StringVar()
        self.account_name = StringVar()
        self.account_type = StringVar(value="asset")

        ttk.Label(form, text="Kontonummer").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.account_number).grid(row=1, column=0, sticky="ew")
        ttk.Label(form, text="Namn").grid(row=0, column=1, sticky="w")
        ttk.Entry(form, textvariable=self.account_name).grid(row=1, column=1, sticky="ew")
        ttk.Label(form, text="Typ").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.account_type,
            values=("asset", "liability", "income", "expense"),
            state="readonly",
        ).grid(row=1, column=2, sticky="ew")
        ttk.Button(form, text="Spara konto", command=self.add_account).grid(row=1, column=3, padx=8)

        for i in range(3):
            form.columnconfigure(i, weight=1)

        self.accounts_tree = ttk.Treeview(
            self.accounts_tab,
            columns=("number", "name", "type"),
            show="headings",
        )
        for col, title in [("number", "Nr"), ("name", "Namn"), ("type", "Typ")]:
            self.accounts_tree.heading(col, text=title)
            self.accounts_tree.column(col, width=260)
        self.accounts_tree.pack(fill="both", expand=True, padx=12, pady=12)

    def _build_vouchers_tab(self) -> None:
        form = ttk.Frame(self.vouchers_tab)
        form.pack(fill="x", padx=12, pady=12)

        self.tx_date = StringVar(value=str(date.today()))
        self.description = StringVar()
        self.debit_account = StringVar()
        self.credit_account = StringVar()
        self.amount = StringVar()

        ttk.Label(form, text="Datum").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.tx_date).grid(row=1, column=0, sticky="ew")
        ttk.Label(form, text="Beskrivning").grid(row=0, column=1, sticky="w")
        ttk.Entry(form, textvariable=self.description).grid(row=1, column=1, sticky="ew")
        ttk.Label(form, text="Debetkonto").grid(row=0, column=2, sticky="w")
        self.debit_combo = ttk.Combobox(form, textvariable=self.debit_account, state="readonly")
        self.debit_combo.grid(row=1, column=2, sticky="ew")
        ttk.Label(form, text="Kreditkonto").grid(row=0, column=3, sticky="w")
        self.credit_combo = ttk.Combobox(form, textvariable=self.credit_account, state="readonly")
        self.credit_combo.grid(row=1, column=3, sticky="ew")
        ttk.Label(form, text="Belopp").grid(row=0, column=4, sticky="w")
        ttk.Entry(form, textvariable=self.amount).grid(row=1, column=4, sticky="ew")
        ttk.Button(form, text="Bokför", command=self.add_voucher).grid(row=1, column=5, padx=8)

        for i in range(5):
            form.columnconfigure(i, weight=1)

    def _build_ledger_tab(self) -> None:
        self.ledger_tree = ttk.Treeview(
            self.ledger_tab,
            columns=("number", "name", "debit", "credit", "net"),
            show="headings",
        )
        for col, title in [
            ("number", "Nr"),
            ("name", "Namn"),
            ("debit", "Debet"),
            ("credit", "Kredit"),
            ("net", "Netto"),
        ]:
            self.ledger_tree.heading(col, text=title)
            self.ledger_tree.column(col, width=180)
        self.ledger_tree.pack(fill="both", expand=True, padx=12, pady=12)

    def add_account(self) -> None:
        try:
            self.db.add_account(self.account_number.get().strip(), self.account_name.get().strip(), self.account_type.get())
            self.account_number.set("")
            self.account_name.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Fel", f"Kunde inte spara konto: {exc}")

    def add_voucher(self) -> None:
        try:
            debit_id = int(self.debit_account.get().split(" - ")[0])
            credit_id = int(self.credit_account.get().split(" - ")[0])
            amount = float(self.amount.get().replace(",", "."))
            if amount <= 0 or debit_id == credit_id:
                raise ValueError("Ogiltig verifikation")

            self.db.add_voucher(self.tx_date.get(), self.description.get().strip(), debit_id, credit_id, amount)
            self.description.set("")
            self.amount.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Fel", f"Kunde inte bokföra verifikation: {exc}")

    def refresh_all(self) -> None:
        summary = self.db.summary()
        for key, label in self.summary_labels.items():
            label.configure(text=f"{(summary[key] or 0):.2f}")

        self._replace_rows(
            self.recent_tree,
            [(r["tx_date"], r["description"], f"{r['total_debit']:.2f}", f"{r['total_credit']:.2f}") for r in self.db.recent_vouchers()],
        )

        accounts = self.db.list_accounts()
        self._replace_rows(self.accounts_tree, [(a.number, a.name, a.type) for a in accounts])

        account_values = [f"{a.id} - {a.number} {a.name}" for a in accounts]
        self.debit_combo["values"] = account_values
        self.credit_combo["values"] = account_values

        self._replace_rows(
            self.ledger_tree,
            [
                (
                    row["number"],
                    row["name"],
                    f"{(row['debit'] or 0):.2f}",
                    f"{(row['credit'] or 0):.2f}",
                    f"{(row['net'] or 0):.2f}",
                )
                for row in self.db.ledger()
            ],
        )

    @staticmethod
    def _replace_rows(tree: ttk.Treeview, rows: list[tuple]) -> None:
        for row_id in tree.get_children():
            tree.delete(row_id)
        for row in rows:
            tree.insert("", END, values=row)


def main() -> None:
    root = Tk()
    db = BookkeepingDB("bookkeeping.db")
    app = BookkeepingApp(root, db)

    def on_close() -> None:
        db.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
