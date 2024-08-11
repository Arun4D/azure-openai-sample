# .NET Customer App

## Building a sample
```console
dotnet build
dotnet run
```

## Install Package
```console
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
dotnet add package Microsoft.SemanticKernel


dotnet tool install --global dotnet-ef --version 8.*
```

## Run Migrations and Update the Database

Initial Migration:
```console
dotnet ef migrations add InitialCreate
dotnet ef database update
```

Update the Database:

```console
dotnet ef database update
```