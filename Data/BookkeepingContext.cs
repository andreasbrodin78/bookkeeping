using BookkeepingApp.Models;
using Microsoft.EntityFrameworkCore;

namespace BookkeepingApp.Data;

public class BookkeepingContext : DbContext
{
    public DbSet<Account> Accounts => Set<Account>();
    public DbSet<Voucher> Vouchers => Set<Voucher>();
    public DbSet<Entry> Entries => Set<Entry>();

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlite("Data Source=bookkeeping.db");
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Account>()
            .HasIndex(a => a.Number)
            .IsUnique();

        modelBuilder.Entity<Account>()
            .HasMany(a => a.Entries)
            .WithOne(e => e.Account)
            .HasForeignKey(e => e.AccountId)
            .OnDelete(DeleteBehavior.Restrict);

        modelBuilder.Entity<Voucher>()
            .HasMany(v => v.Entries)
            .WithOne(e => e.Voucher)
            .HasForeignKey(e => e.VoucherId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Account>()
            .Property(a => a.Type)
            .HasConversion<string>();
    }
}
