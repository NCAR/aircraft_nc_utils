pipeline {
  agent {
     node {
        label 'CentOS8'
        }
  }
  stages {
    stage('Checkout') {
      steps {
        'git config https://github.com/ncar/aircraft_nc_utils.git eolJenkins:ncar/aircraft_nc_utils'
        'git fetch --tags --force --progress -- eolJenkins:ncar/aircraft_nc_utils +refs/heads/*:refs/remotes/origin/*'
        'git rev-parse refs/remotes/origin/master^{commit}'
        'git submodule init'
        'git submodule sync'
        'git config --get https://github.com/ncar/aircraft_nc_utils.git'
        'git submodule init'
        'git config -f .gitmodules --get-regexp ^submodule\.(.+)\.url'
        'git config --get submodule.vardb.url'
        'git config -f .gitmodules --get submodule.vardb.path'
        'git submodule update --init --recursive vardb'
      }
    }
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
