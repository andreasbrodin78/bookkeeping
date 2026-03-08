using System.ComponentModel.DataAnnotations.Schema;

namespace BookkeepingApp.Models;

[Table("Vouchers")]
public class Voucher
{
    public int Id { get; set; }
    public DateOnly TxDate { get; set; }
    public string Description { get; set; } = string.Empty;

    public ICollection<Entry> Entries { get; set; } = new List<Entry>();
}
