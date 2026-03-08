from db import BookkeepingDB


def test_account_and_voucher_flow(tmp_path):
    db = BookkeepingDB(tmp_path / "test.db")

    db.add_account("1930", "Föreningskonto", "asset")
    db.add_account("3010", "Medlemsavgifter", "income")

    accounts = db.list_accounts()
    assert len(accounts) == 2

    db.add_voucher(
        tx_date="2026-01-10",
        description="Avgiftsinbetalning",
        debit_account_id=accounts[0].id,
        credit_account_id=accounts[1].id,
        amount=500.0,
    )

    summary = db.summary()
    assert summary["assets"] == 500.0
    assert summary["income"] == 500.0

    ledger = list(db.ledger())
    assert len(ledger) == 2
    assert any(row["debit"] == 500.0 for row in ledger)

    db.close()
