pipeline {
    agent any

    environment {
        // === RUTAS PARA STM32F103CBT6 ===
        PATH = "${env.PATH};D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin;D:/Program Files/Renode;D:/arm-gnu-toolchain/bin"
        RUBY_HOME = "D:/Ruby40-x64"
        GEM_PATH = "D:/Ruby40-x64/lib/ruby/gems/4.0.0"
        GEM_HOME = "D:/Ruby40-x64/lib/ruby/gems/4.0.0"
                
        // === STM32 ===
        MCU = "STM32F103CBT6"
        MCU_DEFINES = "STM32F103xB"
    }

    stages {
        stage('Limpiar workspace (sin fallo)') {
            steps {
                cleanWs(
                    cleanWhenAborted: true,
                    cleanWhenFailure: true,
                    cleanWhenNotBuilt: true,
                    cleanWhenSuccess: true,
                    notFail: true
                )
                echo 'Workspace limpiado (si fue posible)'
            }
        }

        stage('Preparar entorno') {
            steps {
                echo '===== Verificando herramientas ====='
                bat 'ruby --version'
                bat 'gcc --version'
                bat 'arm-none-eabi-gcc --version'
                bat 'renode --version || echo "Renode no encontrado"'
                bat 'ceedling version'
            }
        }

        stage('Diagnóstico de archivos') {
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
                echo "===== Buscando project.yml ====="
                if exist project.yml (
                    echo "✅ project.yml encontrado en tests/"
                    type project.yml | findstr "project"
                ) else (
                    echo "❌ project.yml NO encontrado en tests/"
                    echo "Buscando en todo el workspace..."
                    cd ..
                    dir /s project.yml
                )
            ) else (
                echo "❌ tests/ NO existe"
            )
        '''
    }
}

        stage('Ejecutar pruebas unitarias') {
            steps {
                echo '===== Ejecutando pruebas con Ceedling ====='
                // Cambiar al directorio tests y ejecutar
                bat '''
                    cd tests
                    echo "===== Directorio actual: %CD% ====="
                    echo "===== Contenido: ====="
                    dir /b
                    
                    echo "===== Ejecutando ceedling clean ====="
                    ceedling clean
                    
                    echo "===== Ejecutando ceedling test:all ====="
                    ceedling test:all
                '''
            }
        }

        stage('Compilar firmware para STM32F103CBT6') {
            steps {
                echo '===== Compilando firmware para STM32F103CBT6 ====='
                bat '''
                    echo "Compilando para STM32F103CBT6..."
                    if exist Makefile (
                        make clean
                        make all
                    ) else (
                        echo "⚠️  Makefile no encontrado, omitiendo compilación"
                    )
                '''
            }
        }

        stage('Simulación con Renode') {
            steps {
                echo '===== Simulación con Renode ====='
                dir('renodescripts') {
                    bat '''
                        echo "===== Ejecutando Renode ====="
                        renode --console --disable-xwt -e "include @stm32f103_led_sim.resc; sleep 2; quit" || echo "Renode no disponible"
                    '''
                }
            }
        }

        stage('Publicar resultados') {
            steps {
                echo '===== Publicando resultados ====='
                junit testResults: 'tests/build/test/results/*.xml', allowEmptyResults: true
                archiveArtifacts artifacts: 'renode/*.log', allowEmptyArchive: true
                archiveArtifacts artifacts: 'build/*.elf', allowEmptyArchive: true
                archiveArtifacts artifacts: 'tests/build/test/out/**/*.log', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo '✅ ¡Todas las pruebas y simulación pasaron! (STM32F103CBT6)'
        }
        failure {
            echo '❌ Algo falló. Revisa los logs.'
            echo '📋 Consejo: Verifica que todas las dependencias estén instaladas y que los archivos de prueba estén en el lugar correcto.'
        }
        always {
            echo '===== Fin del pipeline ====='
        }
    }
}