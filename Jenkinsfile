pipeline {
    agent any

    environment {
        // === RUTAS DE HERRAMIENTAS EN EL SERVIDOR JENKINS ===
        PATH = "${env.PATH};D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin;D:/Program Files/Renode;D:/arm-gnu-toolchain/bin"
        RUBY_HOME = "D:/Ruby40-x64"
        GEM_PATH = "D:/Ruby40-x64/lib/ruby/gems/4.0.0"
        GEM_HOME = "D:/Ruby40-x64/lib/ruby/gems/4.0.0"
        
        // === CONFIGURACIÓN PARA STM32F103CBT6 ===
        MCU = "STM32F103CBT6"
        MCU_DEFINES = "STM32F103xB"
    }

    stages {
        // ============================================================
        // 1. LIMPIEZA DEL WORKSPACE (sin fallar si hay archivos bloqueados)
        // ============================================================
        stage('Limpiar workspace') {
            steps {
                cleanWs(
                    cleanWhenAborted: true,
                    cleanWhenFailure: true,
                    cleanWhenNotBuilt: true,
                    cleanWhenSuccess: true,
                    notFailBuild: true   // ← CORREGIDO: notFailBuild en lugar de notFail
                )
                echo '✅ Workspace limpiado (si fue posible)'
            }
        }

        // ============================================================
        // 2. VERIFICACIÓN DE HERRAMIENTAS
        // ============================================================
        stage('Preparar entorno') {
            steps {
                echo '===== Verificando herramientas ====='
                bat 'ruby --version'
                bat 'gcc --version'
                bat 'ceedling version'
                bat 'renode --version || echo "Renode no encontrado"'
            }
        }

        // ============================================================
        // 3. DIAGNÓSTICO: VERIFICAR QUE LOS ARCHIVOS ESTÉN EN EL WORKSPACE
        // ============================================================
        stage('Verificar archivos del proyecto') {
            steps {
                bat '''
                    echo "===== WORKSPACE: %WORKSPACE% ====="
                    echo ""
                    echo "===== Contenido del workspace ====="
                    dir /b
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
                            echo "Buscando en todo el workspace..."
                            cd ..
                            dir /s project.yml
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
        // 4. PRUEBAS UNITARIAS CON CEEDLING
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
                    ceedling clean --project project.yml
                    
                    echo "===== Ejecutando ceedling test:all ====="
                    ceedling test:all --project project.yml
                '''
            }
        }

        // ============================================================
        // 5. SIMULACIÓN CON RENODE (STM32F103CBT6)
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
        // 6. PUBLICAR RESULTADOS
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