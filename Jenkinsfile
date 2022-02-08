pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  stages {
    stage('Build') {
      steps {
        sh 'git submodule init'
        sh 'git submodule sync'
        sh 'git submodule update --init --recursive vardb'
        
        sh 'scons'
      }
    }
  }
  post {
    always {
      mail(to: 'taylort@ucar.edu', subject: 'nc_utils Jenkins failure', body: 'nc_utils Jenkins failure')
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  triggers {
    pollSCM('H/15 7-20 * * *')
  }
}
