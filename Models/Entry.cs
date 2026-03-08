using System.ComponentModel.DataAnnotations.Schema;

namespace BookkeepingApp.Models;

[Table("Entries")]
public class Entry
{
    public int Id { get; set; }

    public int VoucherId { get; set; }
    public Voucher Voucher { get; set; } = null!;

    public int AccountId { get; set; }
    public Account Account { get; set; } = null!;

    [Column(TypeName = "decimal(18,2)")]
    public decimal Debit { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal Credit { get; set; }
}
