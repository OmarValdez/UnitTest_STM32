pipeline {
    agent any

    environment {
        // Variables de entorno para herramientas
        PATH = "${env.PATH};D:/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi/bin;D:/Ruby40-x64/bin;D:/msys64/ucrt64/bin;D:/Program Files/Renode"
        RUBY_HOME = "D:/Ruby40-x64"
        BUNDLE_PATH = "${WORKSPACE}/vendor/bundle"
        BUNDLE_DISABLE_SHARED_GEMS = "1"
        BUNDLE_GEMFILE = "${WORKSPACE}/Gemfile"
    }

    stages {
        stage('Full Build & Simulation') {
            stages {
                stage('Compile Firmware') {
                    steps {
                        script {
                            // Definir BUILD_TYPE en Groovy
                            env.BUILD_TYPE = "Debug"                    // "Debug" o "Release"
                        }
                        bat '''
                            echo Verifying ARM toolchain...
                            arm-none-eabi-gcc --version
                            cmake --preset %BUILD_TYPE%
                            if exist build\\%BUILD_TYPE% ( cmake --build build\\%BUILD_TYPE% --target clean )
                            cmake --build build\\%BUILD_TYPE% --config %BUILD_TYPE%
                            arm-none-eabi-objcopy -O binary build\\%BUILD_TYPE%\\ST_UnitTest.elf build\\%BUILD_TYPE%\\ST_UnitTest.bin
                        '''
                    }
                }

                stage('Simulacion con Renode') {
                    steps {
                        dir('renodescripts') {
                            bat '''
                                renode --console --disable-xwt -e "include @stm32f103_led_sim.resc" > renode_output.log 2>&1
                            '''
                        }
                    }
                }

                stage('Análisis de cobertura') {
                    steps {
                        dir('tests') {
                            bat '''
                                run_coverage.bat
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            // Publicar artefactos solo si todos los stages pasaron
            archiveArtifacts artifacts: 'build/%BUILD_TYPE%/*.elf, build/%BUILD_TYPE%/*.bin, tests/build/coverage/**/*'
            echo '✅ Full build completed successfully!'
        }
        failure {
            echo '❌ Full build failed. Check Jenkins logs.'
        }
    }
}