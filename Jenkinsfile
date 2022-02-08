pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  stages {
    stage('Build') {
      steps {
        sconsBuild
      }
    }
  }
  post {
    always {
      mail(to: 'taylort@ucar.edu', subject: 'nc_utils Jenkins failyure', body: 'nc_utils Jenkins failure')
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  triggers {
    pollSCM('H/15 7-20 * * *')
  }
}
