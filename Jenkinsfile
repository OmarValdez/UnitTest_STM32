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
                // Se ejecuta dentro del contenedor (root) para evitar problemas
                // de permisos al borrar archivos creados por el contenedor.
                bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest rm -rf build tests/build docs'
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
