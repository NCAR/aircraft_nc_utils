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
        'git --version # timeout=10'
        'git fetch --tags --force --progress -- eolJenkins:ncar/aircraft_nc_utils +refs/heads/*:refs/remotes/origin/* # timeout=10'
        'git rev-parse refs/remotes/origin/master^{commit} # timeout=10'
        'git remote # timeout=10'
        'git submodule init # timeout=10'
        'git submodule sync # timeout=10'
        'git config --get https://github.com/ncar/aircraft_nc_utils.git # timeout=10'
        'git submodule init # timeout=10'
        'git config -f .gitmodules --get-regexp ^submodule\.(.+)\.url # timeout=10'
        'git config --get submodule.vardb.url # timeout=10'
        'git config -f .gitmodules --get submodule.vardb.path # timeout=10'
        'git submodule update --init --recursive vardb # timeout=10'
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
