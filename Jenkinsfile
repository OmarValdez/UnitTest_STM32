pipeline {
    agent any

    stages {
        stage('Construir imagen Docker') {
            steps {
                // Requiere Docker en el agente. El cache de capas acelera rebuilds.
                // Se ejecuta PRIMERO para que la imagen exista antes de usarla.
                bat 'docker build -t sw-medico:latest .'
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
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/simulate.sh'
                    }
                }

                stage('Análisis estático (MISRA-C)') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/static_analysis.sh'
                    }
                }

                stage('Documentación (Doxygen)') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/document.sh'
                    }
                }

                stage('Análisis de cobertura') {
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/coverage.sh'
                    }
                }
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: "build/DockerDebug/*.elf, build/DockerDebug/*.bin, tests/build/coverage/**/*, docs/html/**/*, build/static/**/*"
            echo '✅ Full build completed successfully!'
        }
        failure {
            echo '❌ Full build failed. Check Jenkins logs.'
        }
    }
}
