pipeline {
    agent any

    environment {
        PATH = "${env.PATH};D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin;D:/Program Files/Renode;D:/arm-gnu-toolchain/bin;D:/Program Files/CMake/bin;D:/ninja-win;D:/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi/bin"
        RUBY_HOME = "D:/Ruby40-x64"
        BUNDLE_PATH = "${WORKSPACE}/vendor/bundle"
        BUNDLE_DISABLE_SHARED_GEMS = "1"
        BUNDLE_GEMFILE = "${WORKSPACE}/Gemfile"
    }

    stages {
        stage('Preparar entorno') {
            steps {
                echo '===== Verificando herramientas ====='
                bat 'ruby --version'
                bat 'gcc --version'
                bat 'renode --version || echo "Renode no encontrado"'
                
                echo '===== Configurando Bundler ====='
                bat 'bundle config set path vendor/bundle'
                bat 'bundle config set disable_shared_gems 1'
                bat 'bundle install --jobs 4 --retry 3'
            }
        }

        stage('Compilar firmware') {
            steps {
                script {
                    // Definir BUILD_TYPE en Groovy
                    env.BUILD_TYPE = "Debug"                    // "Debug" o "Release"
                }
                echo '===== Compilando firmware para STM32F103CBT6 ====='
                bat '''
                    echo "===== Limpiando build ====="
                    if exist build (
                        rmdir /s /q build
                    )
                    
                    echo "===== Configurando CMake con preset %BUILD_TYPE% ====="
                    cmake --preset %BUILD_TYPE%

                    if %ERRORLEVEL% NEQ 0 (
                        echo "❌ Error en cmake --preset %BUILD_TYPE%"
                        exit /b 1
                    )
                    
                    echo "===== Compilando ====="
                    cmake --build build/%BUILD_TYPE% --config %BUILD_TYPE%

                    if %ERRORLEVEL% NEQ 0 (
                        echo "❌ Error en la compilación"
                        exit /b 1
                    )
                    
                    echo "===== Verificando .elf ====="
                    if exist build\\%BUILD_TYPE%\\ST_UnitTest.elf (
                        echo "✅ Firmware compilado correctamente"
                    ) else if exist build\\ST_UnitTest.elf (
                        echo "✅ Firmware compilado correctamente (en build/)"
                    ) else (
                        echo "❌ Error: No se encontró el archivo .elf"
                        echo "Buscando archivos .elf en todo el workspace..."
                        dir /s *.elf
                        exit /b 1
                    )
                '''
            }
        }

        stage('Limpiar build de pruebas') {
            steps {
                echo '===== Limpiando build anterior ====='
                bat '''
                    cd %WORKSPACE%\\tests
                    echo "===== Ejecutando ceedling clean ====="
                    bundle exec ceedling clean --project project.yml
                    if %ERRORLEVEL% NEQ 0 (
                        echo "❌ Error en ceedling clean"
                        exit /b %ERRORLEVEL%
                    )
                    echo "✅ ceedling clean completado"
                '''
            }
        }

        stage('Ejecutar pruebas unitarias') {
            steps {
                echo '===== Ejecutando pruebas con Ceedling ====='
                bat '''
                    cd %WORKSPACE%\\tests
                    echo "===== Ejecutando ceedling test:all ====="
                    bundle exec ceedling test:all --project project.yml
                    set CEEDLING_EXIT=%ERRORLEVEL%
                    echo "===== Ceedling test:all finalizado con código: %CEEDLING_EXIT% ====="
                    if %CEEDLING_EXIT% NEQ 0 (
                        echo "❌ Error en ceedling test:all"
                        exit /b %CEEDLING_EXIT%
                    )
                    echo "✅ Todas las pruebas pasaron exitosamente!"
                    echo "===== FIN del stage de pruebas ====="
                '''
            }
        }

        stage('Simulación con Renode') {
            steps {
                echo '===== Simulación con Renode ====='
                dir('renodescripts') {
                    bat '''
                        echo "===== Verificando script de Renode ====="
                        if exist stm32f103_led_sim.resc (
                            echo "✅ Script de Renode encontrado"
                        ) else (
                            echo "❌ Script de Renode NO encontrado"
                            exit /b 1
                        )
                        
                        echo "===== Verificando firmware (.elf) ====="
                        if exist ..\\build\\%BUILD_TYPE%\\ST_UnitTest.elf (
                            echo "✅ Firmware encontrado: ..\\build\\%BUILD_TYPE%\\ST_UnitTest.elf"
                        ) else (
                            echo "⚠️  Firmware NO encontrado"
                        )
                        
                        echo "===== Ejecutando Renode ====="
                        renode --console --disable-xwt -e "include @stm32f103_led_sim.resc" > renode_output.log 2>&1
                        
                        echo "===== Salida de Renode ====="
                        type renode_output.log
                        
                        echo "===== Verificando logs del LED ====="
                        findstr "SIMULACION FINALIZADA" renode_output.log || echo "⚠️  No se termino la simulacion"
                    '''
                }
            }
        }

        stage('Publicar resultados') {
            steps {
                echo '===== Publicando resultados ====='
                junit testResults: 'tests/build/test/results/*.xml', allowEmptyResults: true
                archiveArtifacts artifacts: 'tests/build/test/out/**/*.log', allowEmptyArchive: true
                archiveArtifacts artifacts: 'renodescripts/renode_output.log', allowEmptyArchive: true
                archiveArtifacts artifacts: 'build/Debug/*.elf', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo '✅ ¡Pipeline completado exitosamente!'
        }
        failure {
            echo '❌ Algo falló. Revisa los logs.'
        }
        always {
            echo '===== Fin del pipeline ====='
        }
    }
}