@echo off
echo ===== Ejecutando pruebas con cobertura =====
call bundle exec ceedling test:all --project project.yml
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ceedling fallo al ejecutar las pruebas
    exit /b 1
)

echo ===== Ceedling finalizado correctamente. Continuando... =====

echo ===== Verificando archivos .gcda =====
dir /s build\test\out\*.gcda

echo ===== Creando directorio de reportes =====
if not exist build\coverage mkdir build\coverage

echo ===== Ejecutando gcovr desde MSYS2 =====
D:\msys64\usr\bin\bash.exe -c "cd '%CD%' && export PATH=/ucrt64/bin:$PATH && gcovr --root . --object-directory build/test/out/test_led_logic --gcov-executable gcov --html --html-details -o build/coverage/index.html"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al generar reporte HTML
    exit /b 1
)

echo ===== Generando reporte XML =====
D:\msys64\usr\bin\bash.exe -c "cd '%CD%' && export PATH=/ucrt64/bin:$PATH && gcovr --root . --object-directory build/test/out/test_led_logic --gcov-executable gcov --xml -o build/coverage/coverage.xml"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al generar reporte XML
    exit /b 1
)

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