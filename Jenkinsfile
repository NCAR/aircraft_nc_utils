pipeline {
  agent {
     node {
        label 'CentOS8'
        }
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
    success {
      mail(to: 'cjw@ucar.edu janine@ucar.edu cdewerd@ucar.edu taylort@ucar.edu', subject: 'nc_utils Jenkinsfile build successful', body: 'nc_utils Jenkinsfile build successful')
    }
  }
  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }
  triggers {
    pollSCM('H/15 7-20 * * *')
  }
}
