# git clone https://github.com/bph-tuwien/pythonnet-stub-generator

dotnet run --project pythonnet-stub-generator/csharp/PythonnetStubTool -- --target-dlls src/pypalmsens/_libpalmsens/win/PalmSens.Core.dll --dest-path tmp
mv tmp/PalmSens/* src/PalmSens-stubs/
