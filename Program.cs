using BookkeepingApp.Data;
using BookkeepingApp.Models;
using Microsoft.EntityFrameworkCore;

using var db = new BookkeepingContext();

// Viktig fix för felet "no such table: Accounts"
// Säkerställer att tabeller skapas i SQLite innan någon query körs.
db.Database.EnsureCreated();

Console.WriteLine("Bokföring (lokalt, SQLite)");
Console.WriteLine("Databas: bookkeeping.db");

while (true)
{
    Console.WriteLine("\n1) Lägg till konto");
    Console.WriteLine("2) Bokför verifikation");
    Console.WriteLine("3) Visa konton");
    Console.WriteLine("4) Visa huvudbok");
    Console.WriteLine("0) Avsluta");
    Console.Write("> ");

    var choice = Console.ReadLine();
    switch (choice)
    {
        case "1":
            AddAccount(db);
            break;
        case "2":
            AddVoucher(db);
            break;
        case "3":
            ListAccounts(db);
            break;
        case "4":
            ShowLedger(db);
            break;
        case "0":
            return;
        default:
            Console.WriteLine("Ogiltigt val.");
            break;
    }
}

static void AddAccount(BookkeepingContext db)
{
    Console.Write("Kontonummer: ");
    var number = Console.ReadLine()?.Trim() ?? "";
    Console.Write("Namn: ");
    var name = Console.ReadLine()?.Trim() ?? "";
    Console.Write("Typ (asset/liability/income/expense): ");
    var type = Console.ReadLine()?.Trim() ?? "";

    if (string.IsNullOrWhiteSpace(number) || string.IsNullOrWhiteSpace(name) ||
        !new[] { "asset", "liability", "income", "expense" }.Contains(type))
    {
        Console.WriteLine("Ogiltiga indata.");
        return;
    }

    db.Accounts.Add(new Account { Number = number, Name = name, Type = type });
    try
    {
        db.SaveChanges();
        Console.WriteLine("Konto sparat.");
    }
    catch (DbUpdateException ex)
    {
        Console.WriteLine($"Kunde inte spara konto: {ex.InnerException?.Message ?? ex.Message}");
    }
}

static void AddVoucher(BookkeepingContext db)
{
    var accounts = db.Accounts.OrderBy(a => a.Number).ToList();
    if (accounts.Count < 2)
    {
        Console.WriteLine("Du behöver minst två konton.");
        return;
    }

    foreach (var a in accounts)
    {
        Console.WriteLine($"{a.Id}: {a.Number} - {a.Name}");
    }

    Console.Write("Datum (YYYY-MM-DD): ");
    var dateText = Console.ReadLine();
    Console.Write("Beskrivning: ");
    var desc = Console.ReadLine()?.Trim() ?? "";
    Console.Write("Debet-konto ID: ");
    var debitText = Console.ReadLine();
    Console.Write("Kredit-konto ID: ");
    var creditText = Console.ReadLine();
    Console.Write("Belopp: ");
    var amountText = Console.ReadLine();

    if (!DateOnly.TryParse(dateText, out var txDate) ||
        !int.TryParse(debitText, out var debitId) ||
        !int.TryParse(creditText, out var creditId) ||
        !decimal.TryParse(amountText, out var amount) ||
        amount <= 0 || debitId == creditId || string.IsNullOrWhiteSpace(desc))
    {
        Console.WriteLine("Ogiltig verifikation.");
        return;
    }

    var voucher = new Voucher { TxDate = txDate, Description = desc };
    db.Vouchers.Add(voucher);
    db.SaveChanges();

    db.Entries.AddRange(
        new Entry { VoucherId = voucher.Id, AccountId = debitId, Debit = amount, Credit = 0 },
        new Entry { VoucherId = voucher.Id, AccountId = creditId, Debit = 0, Credit = amount }
    );
    db.SaveChanges();

    Console.WriteLine("Verifikation bokförd.");
}

static void ListAccounts(BookkeepingContext db)
{
    foreach (var a in db.Accounts.OrderBy(a => a.Number))
    {
        Console.WriteLine($"{a.Id}: {a.Number} | {a.Name} | {a.Type}");
    }
}

static void ShowLedger(BookkeepingContext db)
{
    var ledgerRows = db.Accounts
        .Select(a => new
        {
            a.Number,
            a.Name,
            Debit = a.Entries.Sum(e => e.Debit),
            Credit = a.Entries.Sum(e => e.Credit)
        })
        .OrderBy(r => r.Number)
        .ToList();

    foreach (var row in ledgerRows)
    {
        Console.WriteLine($"{row.Number} {row.Name} | Debet: {row.Debit:0.00} | Kredit: {row.Credit:0.00} | Netto: {(row.Debit - row.Credit):0.00}");
    }
}
