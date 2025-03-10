#!/bin/bash -e

# build layers
docker_id=$(
    docker run -d \
        -e PYTHONDONTWRITEBYTECODE=1 \
        public.ecr.aws/sam/build-python3.12 \
            pip install numpy matplotlib \
                -t /tmp/deps \
                --no-cache-dir \
                --root-user-action ignore)

while docker inspect $docker_id --format '{{.State.Running}}' | grep true &>/dev/null; do
    echo -n . && sleep 1
done

rm -rf python numpy-deps.zip
mkdir -p python/lib/python3.12/site-packages/

docker cp $docker_id:/tmp/deps/. python/lib/python3.12/site-packages/
docker rm $docker_id

find python -type d -name '__pycache__' -exec rm -rf {} +

zip -r numpy-deps.zip python
rm -rf python
