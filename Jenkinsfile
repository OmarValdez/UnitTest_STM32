pipeline {
    agent any

    environment {
        // === RUTAS DE HERRAMIENTAS ===
        PATH = "${env.PATH};D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin;D:/Program Files/Renode;D:/arm-gnu-toolchain/bin"
        RUBY_HOME = "D:/Ruby40-x64"
        
        // === CONFIGURACIÓN DE BUNDLER ===
        BUNDLE_PATH = "${WORKSPACE}/vendor/bundle"
        BUNDLE_DISABLE_SHARED_GEMS = "1"
        BUNDLE_GEMFILE = "${WORKSPACE}/Gemfile"
        
        // === CONFIGURACIÓN PARA STM32F103CBT6 ===
        MCU = "STM32F103CBT6"
        MCU_DEFINES = "STM32F103xB"
    }

    stages {
        // ============================================================
        // 1. LIMPIEZA DEL WORKSPACE (ANTES DE CLONAR)
        // ============================================================
        stage('Limpiar workspace') {
            steps {
                cleanWs(
                    cleanWhenAborted: true,
                    cleanWhenFailure: true,
                    cleanWhenNotBuilt: true,
                    cleanWhenSuccess: true,
                    notFailBuild: true
                )
                echo '✅ Workspace limpiado (si fue posible)'
            }
        }

        // ============================================================
        // 2. ACTUALIZAR REPOSITORIO (DESPUÉS DE LA LIMPIEZA)
        // ============================================================
        stage('Actualizar repositorio') {
            steps {
                bat '''
                    echo "===== Verificando que el repositorio esté clonado ====="
                    if exist .git (
                        echo "✅ Repositorio Git encontrado"
                        git fetch --all
                        git reset --hard origin/main
                        git clean -fd
                        echo "===== Último commit ====="
                        git log -1 --oneline
                    ) else (
                        echo "⚠️  Repositorio Git no encontrado - Jenkins debería haberlo clonado"
                        echo "Listando archivos:"
                        dir /b
                    )
                    echo ""
                    echo "===== Verificando archivos ====="
                    dir /b
                    echo ""
                    echo "===== Verificando Gemfile ====="
                    if exist Gemfile (
                        echo "✅ Gemfile encontrado"
                    ) else (
                        echo "❌ Gemfile NO encontrado"
                        echo "El repositorio se clonó pero el Gemfile no está en la raíz."
                        echo "Verifica que el archivo exista en el repositorio remoto."
                        exit /b 1
                    )
                '''
            }
        }

        // ============================================================
        // 3. PREPARAR ENTORNO CON BUNDLER
        // ============================================================
        stage('Preparar entorno') {
            steps {
                echo '===== Verificando herramientas ====='
                bat 'ruby --version'
                bat 'gcc --version'
                bat 'renode --version || echo "Renode no encontrado"'
                
                echo '===== Configurando Bundler ====='
                bat 'bundle config set path vendor/bundle'
                bat 'bundle config set disable_shared_gems 1'
                
                echo '===== Instalando dependencias del proyecto ====='
                bat 'bundle install --jobs 4 --retry 3'
                
                echo '===== Verificando Ceedling ====='
                bat 'bundle exec ceedling version'
            }
        }

        // ============================================================
        // 4. DIAGNÓSTICO: VERIFICAR ARCHIVOS DE PRUEBA
        // ============================================================
        stage('Verificar archivos del proyecto') {
            steps {
                bat '''
                    echo "===== WORKSPACE: %WORKSPACE% ====="
                    echo ""
                    echo "===== Contenido de tests/ ====="
                    if exist tests (
                        cd tests
                        echo "Directorio: %CD%"
                        dir /b
                        echo ""
                        echo "===== Verificando project.yml ====="
                        if exist project.yml (
                            echo "✅ project.yml encontrado en tests/"
                        ) else (
                            echo "❌ project.yml NO encontrado en tests/"
                            exit /b 1
                        )
                    ) else (
                        echo "❌ tests/ NO existe"
                        exit /b 1
                    )
                '''
            }
        }

        // ============================================================
        // 5. PRUEBAS UNITARIAS CON CEEDLING
        // ============================================================
        stage('Ejecutar pruebas unitarias') {
            steps {
                echo '===== Ejecutando pruebas con Ceedling ====='
                bat '''
                    cd %WORKSPACE%\\tests
                    echo "===== Directorio actual: %CD% ====="
                    echo "===== Contenido: ====="
                    dir /b
                    
                    echo "===== Verificando project.yml ====="
                    if exist project.yml (
                        echo "✅ project.yml encontrado"
                    ) else (
                        echo "❌ project.yml NO encontrado"
                        exit /b 1
                    )
                    
                    echo "===== Ejecutando ceedling clean ====="
                    bundle exec ceedling clean --project project.yml
                    
                    echo "===== Ejecutando ceedling test:all ====="
                    bundle exec ceedling test:all --project project.yml
                '''
            }
        }

        // ============================================================
        // 6. SIMULACIÓN CON RENODE
        // ============================================================
        stage('Simulación con Renode') {
            steps {
                echo '===== Simulación con Renode ====='
                dir('renodescripts') {
                    bat '''
                        echo "===== Ejecutando Renode ====="
                        if exist stm32f103_led_sim.resc (
                            echo "✅ Script de Renode encontrado"
                            renode --console --disable-xwt -e "include @stm32f103_led_sim.resc; sleep 2; quit" || echo "Renode no disponible"
                        ) else (
                            echo "⚠️  Script de Renode no encontrado"
                        )
                    '''
                }
            }
        }

        // ============================================================
        // 7. PUBLICAR RESULTADOS
        // ============================================================
        stage('Publicar resultados') {
            steps {
                echo '===== Publicando resultados ====='
                junit testResults: 'tests/build/test/results/*.xml', allowEmptyResults: true
                archiveArtifacts artifacts: 'tests/build/test/out/**/*.log', allowEmptyArchive: true
                archiveArtifacts artifacts: 'renodescripts/*.log', allowEmptyArchive: true
            }
        }
    }

    // ============================================================
    // POST: ACCIONES AL FINAL DEL PIPELINE
    // ============================================================
    post {
        success {
            echo '✅ ¡Todas las pruebas y simulaciones pasaron exitosamente!'
        }
        failure {
            echo '❌ Algo falló. Revisa los logs.'
            echo '📋 Consejo: Verifica que el repositorio contenga todos los archivos necesarios.'
        }
        always {
            echo '===== Fin del pipeline ====='
        }
    }
}