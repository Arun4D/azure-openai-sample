using Microsoft.EntityFrameworkCore;
using sk_backend_api.Model;

namespace sk_backend_api.Data
{
    public class ApplicationDbContext: DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext>options): base(options) { }
        public DbSet<Customer> Customers { get; set; }
    }
}
