pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  triggers {
  pollSCM('H/15 7-20 * * *')
  }
  stages {
    stage('Build') {
      steps {
        sh 'git submodule update --init --recursive vardb'
        sh 'scons install'
      }
    }
  }
  post {
    always {
      emailext to: "taylort@ucar.edu",
      subject: "Jenkinsfile aircraft_nc_utils build complete",
      body: "See console output attached",
      attachLog: true
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}
