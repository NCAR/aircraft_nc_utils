pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  stages {
    stage('Build') {
      steps {
        sconsBuild parallel_build: true,
         scons_exe: 'scons-3'
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
