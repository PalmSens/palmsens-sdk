# PalmSens Core DLL updator

This directory contains a shim build project that gets grabs all dll dependencies for PyPalmSens.

`dotnet publish` with targeted Runtime Identifiers (RIDs) lets NuGet resolve the correct transitive dependencies from nuget.org while pulling our own packages from a local directory.

| File | Purpose |
|------|---------|
| `Program.cs` | Dummy entry point required by the executable shim. |
| `windows.csproj` | References `PalmSens.Core` + `PalmSens.Core.Windows`. Publishes for Windows runtime. |
| `mono.csproj` | References `PalmSens.Core` + `PalmSens.Core.Linux`. Publishes for Linux / macOS runtimes. |
| `update.py` | Manages `dotnet publish` calls and sorts the outputs into per-platform directories. |

## Prerequisites

- Local packages placed in `C:\Packages` (or another directory you configure):
  - `PalmSens.Core`
  - `PalmSens.Core.Windows`
  - `PalmSens.Core.Linux`

## Configure the Local NuGet Source

Before running `update.py`, register the local directory with the .NET SDK so NuGet:

```powershell
dotnet nuget add source "C:\Packages" --name "PalmSensLocal"
```

If you move the folder, update the source:

```powershell
dotnet nuget update source "PalmSensLocal" --source "C:\Packages"
```

## Usage

For new versions:

1. Add the nuget versions to C:/Packages
2. Update the versions in `windows.csproj`, `mono.csproj`

Run the extractor from the repository root:

```powershell
python update.py
```

The script will execute five publish operations in total:

| # | Project | RID | Output contains |
|---|---------|-----|-----------------|
| 1 | `windows.csproj` | `win-x64` | Managed DLLs + Windows native DLLs |
| 2 | `mono.csproj` | `linux-x64` | Managed DLLs + Linux x64 native `.so` files |
| 3 | `mono.csproj` | `linux-arm64` | Managed DLLs + Linux ARM64 native `.so` files |
| 4 | `mono.csproj` | `osx-x64` | Managed DLLs + macOS x64 native `.dylib` files |
| 5 | `mono.csproj` | `osx-arm64` | Managed DLLs + macOS ARM64 native `.dylib` files |

The resulting DLLs and native libraries are placed in the platform-specific directories defined by the script in `src/pypalmsens/_libpalmsens/`
