#!/bin/bash -e


CURRENT_DIR=`pwd`
DOTNET_TRACER_DIR=$HOME/dd/dd-trace-dotnet

(
    # if is not symlink
    if [ ! -h /ddlogs ]; then
        echo "Directory /ddlogs does not exist!  On mac, create one using:"
        echo "https://www.igorkromin.net/index.php/2020/02/19/how-to-create-symlinks-at-the-macos-1015-catalina-root-file-system/"
        exit 1
    fi

    cd $DOTNET_TRACER_DIR/tracer
    # force linux/amd64 docker containers to avoid problems with arm64
    DOCKER_DEFAULT_PLATFORM=linux/amd64 ./build_in_docker.sh BuildTracerHome

    cd $CURRENT_DIR
    rm -rf datadog dotnet-tracer-*.zip
    cp -r $DOTNET_TRACER_DIR/shared/bin/monitoring-home $CURRENT_DIR/datadog

    sha=$(git rev-parse HEAD)
    datetime=$(date '+%Y%m%d%H%M')
    zip -r dotnet-tracer-${datetime}-${sha:0:7}.zip datadog
)
