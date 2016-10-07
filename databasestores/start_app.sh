#!/bin/bash -e

if [[ -z $PYAGENT_DIR ]]
then
    echo 'Please set env var PYAGENT_DIR'
    exit 1
fi

pushd $PYAGENT_DIR
rm dist/* || true
make sdist || exit 1
popd

rm dist/* || true
cp $PYAGENT_DIR/dist/*.tar.gz dist/

docker build -t app .
docker run -it --volume `pwd`:/data --net=host app
