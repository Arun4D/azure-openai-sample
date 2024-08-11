using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Hosting;
using sk_backend_api.Data;
using System.Configuration;

var builder = WebApplication.CreateBuilder(args);

// Add Environment Variable
builder.Configuration
    .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
    .AddEnvironmentVariables(prefix: "ASPNETCORE_")
    .AddEnvironmentVariables(prefix: "DOTNET_")
    .AddEnvironmentVariables()
    .AddCommandLine(args);

// Add Db context
builder.Services.AddDbContext<ApplicationDbContext>(options =>
options.UseSqlite("Data Source=customer.db"));

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
