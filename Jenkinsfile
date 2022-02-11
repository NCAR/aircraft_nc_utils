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
        sh 'scons'
      }
    }
  }
  post {
    failure {
      mail(to: 'cjw@ucar.edu janine@ucar.edu cdewerd@ucar.edu taylort@ucar.edu', subject: 'nc_utils Jenkinsfile build failed', body: 'nc_utils Jenkinsfile build failed')
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
}
