pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  stages {

    stage('Build') {
      steps {
        'scons'
      }
    }
  }
  post {
    always {
      mail(to: 'taylort@ucar.edu', body: 'nc_utils Jenkins failure')
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  triggers {
    pollSCM('H/15 7-20 * * *')
  }
}
