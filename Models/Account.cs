using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace BookkeepingApp.Models;

[Table("Accounts")]
public class Account
{
    public int Id { get; set; }

    [MaxLength(20)]
    public string Number { get; set; } = string.Empty;

    [MaxLength(120)]
    public string Name { get; set; } = string.Empty;

    [MaxLength(20)]
    public string Type { get; set; } = string.Empty;

    public ICollection<Entry> Entries { get; set; } = new List<Entry>();
}
