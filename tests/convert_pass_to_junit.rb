#!/usr/bin/env ruby
# ============================================================
# CONVERTIR EL ARCHIVO .pass DE CEEDLING A JUNIT XML
# VERSIÓN MEJORADA - MANEJA DIFERENTES FORMATOS
# ============================================================

require 'yaml'
require 'json'

# ============================================================
# CONFIGURACIÓN
# ============================================================
PASS_FILE = 'build/test/results/test_led_logic.pass'
XML_FILE = 'build/test/results/junit_report.xml'

# ============================================================
# FUNCIÓN PARA PARSEAR EL .pass (FLEXIBLE)
# ============================================================
def parse_pass_file(file_path)
  content = File.read(file_path)
  
  # Intentar parsear como YAML
  begin
    data = YAML.load(content)
    return data if data && data.is_a?(Hash)
  rescue
    # Si falla, intentar con formato alternativo
  end
  
  # Si no es YAML, intentar con JSON
  begin
    data = JSON.parse(content)
    return data if data && data.is_a?(Hash)
  rescue
    # Si falla, intentar parseo manual
  end
  
  # Si todo falla, intentar parseo manual de campos clave
  data = {}
  data['successes'] = []
  data['failures'] = []
  data['ignores'] = []
  data['counts'] = {}
  data['time'] = 0
  data['source'] = {}
  
  # Buscar campos comunes
  if content =~ /:successes:\s*-\s*:test:\s*(.*?)\s*:line:\s*(\d+)/m
    # Formato YAML simple
    content.scan(/:successes:\s*-\s*:test:\s*(.*?)\s*:line:\s*(\d+)/m) do |match|
      data['successes'] << { 'test' => match[0].strip, 'line' => match[1].to_i }
    end
    content.scan(/:failures:\s*-\s*:test:\s*(.*?)\s*:line:\s*(\d+)/m) do |match|
      data['failures'] << { 'test' => match[0].strip, 'line' => match[1].to_i }
    end
    content.scan(/:ignores:\s*-\s*:test:\s*(.*?)\s*:line:\s*(\d+)/m) do |match|
      data['ignores'] << { 'test' => match[0].strip, 'line' => match[1].to_i }
    end
    content =~ /:total:\s*(\d+)/
    data['counts']['total'] = $1.to_i if $1
    content =~ /:passed:\s*(\d+)/
    data['counts']['passed'] = $1.to_i if $1
    content =~ /:failed:\s*(\d+)/
    data['counts']['failed'] = $1.to_i if $1
    content =~ /:ignored:\s*(\d+)/
    data['counts']['ignored'] = $1.to_i if $1
    content =~ /:time:\s*([\d.]+)/
    data['time'] = $1.to_f if $1
  end
  
  data
end

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def convert_pass_to_junit(pass_file, xml_file)
  # Verificar que el archivo .pass existe
  unless File.exist?(pass_file)
    puts "⚠️  Archivo .pass no encontrado: #{pass_file}"
    return false
  end

  # Leer y parsear el archivo
  data = parse_pass_file(pass_file)
  
  # Verificar que los datos sean válidos
  unless data && data.is_a?(Hash)
    puts "⚠️  No se pudo parsear el archivo .pass"
    return false
  end

  # Extraer información (con valores por defecto)
  successes = data['successes'] || []
  failures = data['failures'] || []
  ignores = data['ignores'] || []
  
  # Si successes es un hash, convertirlo a array
  if successes.is_a?(Hash)
    successes = [successes]
  end
  
  # Si failures es un hash, convertirlo a array
  if failures.is_a?(Hash)
    failures = [failures]
  end
  
  # Si ignores es un hash, convertirlo a array
  if ignores.is_a?(Hash)
    ignores = [ignores]
  end

  # Contar pruebas
  total = successes.size + failures.size + ignores.size
  passed = successes.size
  failed = failures.size
  ignored = ignores.size

  # Si no se encontraron pruebas, usar los counts del archivo
  if total == 0
    total = data.dig('counts', 'total') || 0
    passed = data.dig('counts', 'passed') || 0
    failed = data.dig('counts', 'failed') || 0
    ignored = data.dig('counts', 'ignored') || 0
  end

  # Obtener el nombre del archivo de prueba
  source_file = data.dig('source', 'basename') || 'unknown'
  classname = File.basename(source_file, '.*')
  if classname.nil? || classname.empty?
    classname = 'test_led_logic'
  end

  # Tiempo de ejecución
  time = data['time'] || 0

  puts "📊 Resultados encontrados:"
  puts "   Total: #{total}, Pasadas: #{passed}, Fallidas: #{failed}, Ignoradas: #{ignored}"

  # ============================================================
  # GENERAR XML
  # ============================================================
  File.open(xml_file, 'w') do |f|
    f.puts '<?xml version="1.0" encoding="UTF-8"?>'
    f.puts '<testsuites>'
    f.puts "  <testsuite name=\"#{classname}\" tests=\"#{total}\" failures=\"#{failed}\" errors=\"0\" skipped=\"#{ignored}\" time=\"#{time}\">"

    # Agregar pruebas exitosas
    successes.each do |test|
      if test.is_a?(Hash)
        name = test['test'] || test[:test] || 'unknown'
        line = test['line'] || test[:line] || 0
      else
        name = test.to_s
        line = 0
      end
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\"/>"
    end

    # Agregar pruebas fallidas
    failures.each do |test|
      if test.is_a?(Hash)
        name = test['test'] || test[:test] || 'unknown'
        line = test['line'] || test[:line] || 0
        message = test['message'] || test[:message] || 'Test failed'
      else
        name = test.to_s
        line = 0
        message = 'Test failed'
      end
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\">"
      f.puts "      <failure message=\"#{message}\"/>"
      f.puts "    </testcase>"
    end

    # Agregar pruebas ignoradas
    ignores.each do |test|
      if test.is_a?(Hash)
        name = test['test'] || test[:test] || 'unknown'
        line = test['line'] || test[:line] || 0
      else
        name = test.to_s
        line = 0
      end
      f.puts "    <testcase name=\"#{name}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{line}\">"
      f.puts "      <skipped/>"
      f.puts "    </testcase>"
    end

    f.puts '  </testsuite>'
    f.puts '</testsuites>'
  end

  puts "✅ Reporte JUnit generado en: #{xml_file}"
  true
end

# ============================================================
# EJECUCIÓN
# ============================================================
if __FILE__ == $0
  puts "===== Convertiendo .pass a JUnit XML ====="
  success = convert_pass_to_junit(PASS_FILE, XML_FILE)
  
  if success
    puts "✅ Conversión completada exitosamente"
    exit 0
  else
    puts "❌ Error en la conversión"
    exit 1
  end
end