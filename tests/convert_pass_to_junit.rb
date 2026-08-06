#!/usr/bin/env ruby
# ============================================================
# CONVERTIR .pass A JUNIT XML - VERSIÓN SIMPLIFICADA
# ============================================================

PASS_FILE = 'build/test/results/test_led_logic.pass'
XML_FILE = 'build/test/results/junit_report.xml'

def convert_pass_to_junit(pass_file, xml_file)
  unless File.exist?(pass_file)
    puts "⚠️  Archivo .pass no encontrado"
    generate_empty_xml(xml_file)
    return false
  end

  puts "📖 Leyendo archivo: #{pass_file}"
  content = File.read(pass_file)
  
  # Extraer el nombre del archivo de prueba (source)
  source_match = content.match(/basename:\s*(.*)/)
  source_file = source_match ? source_match[1].strip : 'unknown'
  classname = File.basename(source_file, '.*')
  
  # Extraer información de las pruebas
  tests = []
  
  # Buscar todas las pruebas exitosas
  content.scan(/- :test: (.*?)\n\s+:line: (\d+)/) do |name, line|
    tests << { name: name.strip, line: line.to_i, status: 'pass' }
  end
  
  # Buscar pruebas fallidas (si existen)
  content.scan(/- :test: (.*?)\n\s+:line: (\d+)\n\s+:message: (.*?)\n/m) do |name, line, msg|
    tests << { name: name.strip, line: line.to_i, status: 'fail', message: msg.strip }
  end
  
  # Extraer conteos
  total_match = content.match(/:total:\s*(\d+)/)
  passed_match = content.match(/:passed:\s*(\d+)/)
  failed_match = content.match(/:failed:\s*(\d+)/)
  ignored_match = content.match(/:ignored:\s*(\d+)/)
  time_match = content.match(/:time:\s*([\d.]+)/)
  
  total = total_match ? total_match[1].to_i : tests.size
  passed = passed_match ? passed_match[1].to_i : tests.count { |t| t[:status] == 'pass' }
  failed = failed_match ? failed_match[1].to_i : tests.count { |t| t[:status] == 'fail' }
  ignored = ignored_match ? ignored_match[1].to_i : 0
  time = time_match ? time_match[1].to_f : 0

  puts "📊 Resultados: Total=#{total}, Pasadas=#{passed}, Fallidas=#{failed}, Ignoradas=#{ignored}"

  # ============================================================
  # GENERAR XML
  # ============================================================
  File.open(xml_file, 'w') do |f|
    f.puts '<?xml version="1.0" encoding="UTF-8"?>'
    f.puts '<testsuites>'
    f.puts "  <testsuite name=\"#{classname}\" tests=\"#{total}\" failures=\"#{failed}\" errors=\"0\" skipped=\"#{ignored}\" time=\"#{time}\">"

    # Agregar cada prueba
    tests.each do |test|
      if test[:status] == 'pass'
        f.puts "    <testcase name=\"#{test[:name]}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{test[:line]}\"/>"
      else
        f.puts "    <testcase name=\"#{test[:name]}\" classname=\"#{classname}\" time=\"0.001\" line=\"#{test[:line]}\">"
        f.puts "      <failure message=\"#{test[:message] || 'Test failed'}\"/>"
        f.puts "    </testcase>"
      end
    end

    f.puts '  </testsuite>'
    f.puts '</testsuites>'
  end

  puts "✅ Reporte JUnit generado en: #{xml_file}"
  true
end

def generate_empty_xml(xml_file)
  File.open(xml_file, 'w') do |f|
    f.puts '<?xml version="1.0" encoding="UTF-8"?>'
    f.puts '<testsuites>'
    f.puts '  <testsuite name="unknown" tests="0" failures="0" errors="0" skipped="0" time="0">'
    f.puts '  </testsuite>'
    f.puts '</testsuites>'
  end
end

# ============================================================
# EJECUCIÓN
# ============================================================
if __FILE__ == $0
  puts "===== Convertiendo .pass a JUnit XML ====="
  success = convert_pass_to_junit(PASS_FILE, XML_FILE)
  exit(success ? 0 : 1)
end