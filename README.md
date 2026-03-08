# Bokföring för mindre föreningar (.NET + SQLite)

Det här är ett lokalt bokföringsprogram för PC byggt med **C#/.NET** och **SQLite**.

## Viktig fix för felet
Om du har fått:

`SQLite Error 1: 'no such table: Accounts'`

så är det normalt att databasen inte hunnit skapa tabeller ännu. I denna version körs:

- `db.Database.EnsureCreated();`

vid uppstart, vilket automatiskt skapar `Accounts`, `Vouchers` och `Entries` i `bookkeeping.db`.

## Starta
1. Installera .NET SDK 8.
2. Kör:

```bash
dotnet restore
dotnet run
```

Programmet körs i terminalen och sparar data lokalt i `bookkeeping.db`.

## Funktioner
- Lägg till konton.
- Bokför verifikationer (debet/kredit).
- Lista konton.
- Visa enkel huvudbok.
