@echo off
echo ===== Ejecutando pruebas con cobertura =====
bundle exec ceedling test:all --project project.yml

echo ===== Verificando archivos .gcda =====
dir /s build\test\out\*.gcda

echo ===== Generando reporte HTML =====
D:\msys64\ucrt64\bin\gcovr.exe --root . --object-directory build\test\out\test_led_logic --gcov-executable "D:\msys64\ucrt64\bin\gcov.exe" --html --html-details -o build\coverage\index.html

echo ===== Generando reporte XML =====
D:\msys64\ucrt64\bin\gcovr.exe --root . --object-directory build\test\out\test_led_logic --gcov-executable "D:\msys64\ucrt64\bin\gcov.exe" --xml -o build\coverage\coverage.xml

echo ===== Verificando reportes =====
if exist build\coverage\index.html (
    echo ✅ Reporte HTML generado
) else (
    echo ❌ No se generó reporte HTML
    exit /b 1
)

if exist build\coverage\coverage.xml (
    echo ✅ Reporte XML generado
) else (
    echo ❌ No se generó reporte XML
    exit /b 1
)

echo ✅ Reportes generados correctamente
dir build\coverage\