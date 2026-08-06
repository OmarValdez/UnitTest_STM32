#!/usr/bin/env ruby
# ============================================================
# CONVERTIR EL ARCHIVO .pass DE CEEDLING A JUNIT XML
# ============================================================

require 'yaml'
require 'time'

# ============================================================
# CONFIGURACIÓN
# ============================================================
PASS_FILE = 'build/test/results/test_led_logic.pass'
XML_FILE = 'build/test/results/junit_report.xml'

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def convert_pass_to_junit(pass_file, xml_file)
  # Verificar que el archivo .pass existe
  unless File.exist?(pass_file)
    puts "⚠️  Archivo .pass no encontrado: #{pass_file}"
    return false
  end

  # Leer el archivo YAML
  data = YAML.load_file(pass_file)

  # Verificar que los datos sean válidos
  unless data && data.is_a?(Hash) && data.key?('successes')
    puts "⚠️  El archivo .pass no tiene el formato esperado"
    return false
  end

  # Extraer información
  successes = data['successes'] || []
  failures = data['failures'] || []
  ignores = data['ignores'] || []
  total = data.dig('counts', 'total') || 0
  passed = data.dig('counts', 'passed') || 0
  failed = data.dig('counts', 'failed') || 0
  ignored = data.dig('counts', 'ignored') || 0
  time = data['time'] || 0

  # Obtener el nombre del archivo de prueba
  source_file = data.dig('source', 'basename') || 'unknown'
  classname = File.basename(source_file, '.*')

  # ============================================================
  # GENERAR XML
  # ============================================================
  File.open(xml_file, 'w') do |f|
    f.puts '<?xml version="1.0" encoding="UTF-8"?>'
    f.puts '<testsuites>'
    f.puts "  <testsuite name=\"#{classname}\" tests=\"#{total}\" failures=\"#{failed}\" errors=\"0\" skipped=\"#{ignored}\" time=\"#{time}\">"

    # Agregar pruebas exitosas
    successes.each do |test|
      name = test['test'] || 'unknown'
      line = test['line'] || 0
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\"/>"
    end

    # Agregar pruebas fallidas
    failures.each do |test|
      name = test['test'] || 'unknown'
      line = test['line'] || 0
      message = test['message'] || 'Test failed'
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\">"
      f.puts "      <failure message=\"#{message}\"/>"
      f.puts "    </testcase>"
    end

    # Agregar pruebas ignoradas
    ignores.each do |test|
      name = test['test'] || 'unknown'
      line = test['line'] || 0
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\">"
      f.puts "      <skipped/>"
      f.puts "    </testcase>"
    end

    f.puts '  </testsuite>'
    f.puts '</testsuites>'
  end

  puts "✅ Reporte JUnit generado en: #{xml_file}"
  puts "   Total: #{total}, Pasadas: #{passed}, Fallidas: #{failed}, Ignoradas: #{ignored}"
  true
end

# ============================================================
# EJECUCIÓN
# ============================================================
if __FILE__ == $0
  success = convert_pass_to_junit(PASS_FILE, XML_FILE)
  exit(success ? 0 : 1)
end