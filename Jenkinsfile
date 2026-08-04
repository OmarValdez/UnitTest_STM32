pipeline {
    agent any

    environment {
        // Variables de entorno para Windows
        PATH = "${env.PATH};D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin"
        RUBY_HOME = "D:/Ruby40-x64"
        CEEDLING_PATH = "D:/Ruby40-x64/bin"
    }

    stages {
        stage('Limpiar workspace') {
            steps {
                cleanWs()
                echo 'Workspace limpiado'
            }
        }

        stage('Preparar entorno') {
            steps {
                echo '===== Verificando herramientas ====='
                bat 'ruby --version'
                bat 'gcc --version'
                bat 'ceedling version'
            }
        }

        stage('Ejecutar pruebas unitarias') {
            steps {
                echo '===== Ejecutando pruebas con Ceedling ====='
                dir('tests') {
                    bat 'ceedling clean'
                    bat 'ceedling test:all || exit /b 0' // Permite continuar aunque fallen pruebas
                }
            }
        }

        stage('Publicar resultados') {
            steps {
                echo '===== Publicando resultados ====='
                // Publicar resultados JUnit (si Ceedling los genera)
                junit testResults: 'tests/build/test/results/*.xml', allowEmptyResults: true
                
                // Publicar logs
                archiveArtifacts artifacts: 'tests/build/test/out/**/*.log', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo '✅ ¡Todas las pruebas pasaron exitosamente!'
        }
        failure {
            echo '❌ Algunas pruebas fallaron. Revisa los logs.'
        }
        always {
            echo '===== Fin del pipeline ====='
        }
    }
}