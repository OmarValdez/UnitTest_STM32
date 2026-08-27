pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 90, unit: 'MINUTES')
    }

    // === MACROS / TOOGLES DE CALIDAD ===
    // Cada analisis se puede activar/desactivar y, donde aplica, fijar su
    // nivel/umbral. Estos parametros aparecen en la UI del job (y por rama en
    // Multibranch) para activarlos/ajustarlos sin editar el codigo.
    parameters {
        booleanParam(name: 'RUN_CPPCHECK',     defaultValue: true, description: 'cppcheck + estilo (calidad)')
        booleanParam(name: 'RUN_MISRA',        defaultValue: true, description: 'MISRA-C:2012 (requiere reglas licenciadas en config/)')
        booleanParam(name: 'RUN_COMPLEXITY',   defaultValue: true, description: 'Complejidad ciclomatica (lizard, CCN>10)')
        booleanParam(name: 'RUN_FLAWFINDER',   defaultValue: true, description: 'Analisis de seguridad flawfinder (solo Core/User + main)')
        choice(name: 'FLAWFINDER_MINLEVEL', choices: ['1','2','3','4','5'], description: 'Nivel minimo de riesgo flawfinder (1=bajo .. 5=alto)')
        booleanParam(name: 'RUN_COVERAGE',     defaultValue: true, description: 'Cobertura con gcovr')
        string(name: 'COVERAGE_THRESHOLD', defaultValue: '80', description: 'Umbral minimo de cobertura de lineas (%) para el quality gate')
        booleanParam(name: 'RUN_SIM',          defaultValue: true, description: 'Simulacion en Renode')
        booleanParam(name: 'RUN_DOCS',         defaultValue: true, description: 'Documentacion Doxygen')
    }

    // Dispara automaticamente ante cada push sin depender de webhooks de
    // GitHub: como Jenkins queda en la LAN (IP privada), los webhooks de
    // GitHub cloud no pueden alcanzarlo. El polling SCM hace que Jenkins
    // consulte el repo periodicamente y construya al detectar cambios.
    // En un job Multibranch este trigger se ignora; usar "Branch Indexing"
    // periodico (p.ej. cada 1-2 min) en la config del job.
    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        RUN_CPPCHECK       = "${params.RUN_CPPCHECK ? '1' : '0'}"
        RUN_MISRA          = "${params.RUN_MISRA ? '1' : '0'}"
        RUN_COMPLEXITY     = "${params.RUN_COMPLEXITY ? '1' : '0'}"
        RUN_FLAWFINDER     = "${params.RUN_FLAWFINDER ? '1' : '0'}"
        FLAWFINDER_MINLEVEL = "${params.FLAWFINDER_MINLEVEL}"
        RUN_COVERAGE       = "${params.RUN_COVERAGE ? '1' : '0'}"
        COVERAGE_THRESHOLD = "${params.COVERAGE_THRESHOLD}"
        RUN_SIM            = "${params.RUN_SIM ? '1' : '0'}"
        RUN_DOCS           = "${params.RUN_DOCS ? '1' : '0'}"
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
                    when { expression { params.RUN_SIM } }
                    steps {
                        // Timeout para evitar que Renode cuelgue el pipeline.
                        timeout(time: 5, unit: 'MINUTES') {
                            bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/simulate.sh'
                        }
                    }
                }

                stage('Analisis estatico (MISRA-C)') {
                    steps {
                        bat 'docker run --rm -e RUN_CPPCHECK -e RUN_MISRA -e RUN_COMPLEXITY -e RUN_FLAWFINDER -e FLAWFINDER_MINLEVEL -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/static_analysis.sh'
                    }
                }

                stage('Documentacion (Doxygen)') {
                    when { expression { params.RUN_DOCS } }
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/document.sh'
                    }
                }

                stage('Analisis de cobertura') {
                    when { expression { params.RUN_COVERAGE } }
                    steps {
                        bat 'docker run --rm -v "%WORKSPACE%:/work" -w /work sw-medico:latest bash /work/ci/coverage.sh'
                    }
                }

                stage('Quality Gate: Cobertura') {
                    when { expression { params.RUN_COVERAGE } }
                    steps {
                        // Falla el build si la cobertura de lineas esta por
                        // debajo de COVERAGE_THRESHOLD (macro configurable).
                        bat 'docker run --rm -e COVERAGE_THRESHOLD -v "%WORKSPACE%:/work" -w /work sw-medico:latest python3 /work/ci/coverage_gate.py'
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
                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                 reportDir: 'build/coverage', reportFiles: 'index.html', reportName: 'Coverage'])
                } catch (e) { echo "HTML Publisher plugin faltante para Coverage: ${e}" }
                try {
                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true,
                                 reportDir: 'build/static', reportFiles: 'index.html', reportName: 'Static Analysis'])
                } catch (e) { echo "HTML Publisher plugin faltante para Static Analysis: ${e}" }
            }
        }
        failure {
            echo '❌ Full build failed. Check Jenkins logs.'
        }
    }
}
