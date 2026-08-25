pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 90, unit: 'MINUTES')
    }

    stages {
        stage('Construir imagen Docker') {
            steps {
                // Requiere Docker en el agente. Reconstruye solo si la imagen no
                // existe o si cambiaron Dockerfile/Gemfile/config (que si se hornean
                // en la imagen). Los scripts ci/ se montan en runtime, no requieren
                // rebuild. El cache de capas de Docker acelera los rebuilds.
                bat '''
                    set REBUILD=0
                    docker image inspect sw-medico:latest >nul 2>&1 || set REBUILD=1
                    git diff --quiet origin/main -- Dockerfile Gemfile config 2>nul || set REBUILD=1
                    if "%REBUILD%"=="1" (
                        docker build -t sw-medico:latest .
                    ) else (
                        echo Imagen sw-medico:latest al dia; se reutiliza el cache de capas.
                    )
                '''
            }
        }

        stage('Limpieza de artefactos') {
            steps {
                // Limpieza en el HOST (Windows). Borrar desde el contenedor
                // falla con "Permission denied" en bind-mounts 9p de Docker
                // Desktop (los archivos creados por Linux no se borran como root).
                // del /f fuerza archivos read-only; rmdir /s /q quita el arbol.
                bat '''
                    if exist build ( del /f /s /q build & rmdir /s /q build )
                    if exist tests\\build ( del /f /s /q tests\\build & rmdir /s /q tests\\build )
                    if exist docs ( del /f /s /q docs & rmdir /s /q docs )
                '''
            }
        }

        stage('Normalizar scripts (CRLF -> LF)') {
            steps {
                // Se ejecuta en el HOST (Windows) porque Docker Desktop no
                // permite renombrar/borrar en bind-mounts 9p desde el
                // contenedor. Convierte CRLF -> LF para que bash no falle.
                bat 'powershell -NoProfile -ExecutionPolicy Bypass -File ci/normalize_eol.ps1'
            }
        }

        stage('Full Build & Simulation') {
            stages {
                stage('Compile Firmware') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/compile.sh'
                    }
                }

                stage('Simulacion con Renode') {
                    steps {
                        // Timeout para evitar que Renode cuelgue el pipeline.
                        timeout(time: 5, unit: 'MINUTES') {
                            bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/simulate.sh'
                        }
                    }
                }

                stage('Analisis estatico (MISRA-C)') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/static_analysis.sh'
                    }
                }

                stage('Documentacion (Doxygen)') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/document.sh'
                    }
                }

                stage('Analisis de cobertura') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/coverage.sh'
                    }
                }
            }
        }
    }

    post {
        always {
            // Publica resultados JUnit de Ceedling (requiere plugin JUnit).
            script {
                try {
                    junit 'tests/build/artifacts/test/*.xml'
                } catch (e) {
                    echo "Advertencia: no se publicaron resultados JUnit (¿plugin faltante?): ${e}"
                }
            }
        }
        success {
            echo '✅ Full build completed successfully!'
            // Fix: la cobertura se escribe en build/coverage (no tests/build/coverage).
            archiveArtifacts artifacts: "build/DockerDebug/*.elf, build/DockerDebug/*.bin, build/coverage/**/*, docs/html/**/*, build/static/**/*"
            script {
                // publishHTML requiere el plugin "HTML Publisher".
                try {
                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                 reportDir: 'docs/html', reportFiles: 'index.html', reportName: 'Doxygen'])
                } catch (e) { echo "HTML Publisher plugin faltante para Doxygen: ${e}" }
                try {
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true,
                                 reportDir: 'build/coverage', reportFiles: 'index.html', reportName: 'Coverage'])
                } catch (e) { echo "HTML Publisher plugin faltante para Coverage: ${e}" }
                try {
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true,
                                 reportDir: 'build/static', reportFiles: 'cppcheck.xml', reportName: 'Cppcheck'])
                } catch (e) { echo "HTML Publisher plugin faltante para Cppcheck: ${e}" }
            }
        }
        failure {
            echo '❌ Full build failed. Check Jenkins logs.'
        }
    }
}
