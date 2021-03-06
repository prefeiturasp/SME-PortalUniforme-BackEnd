#!/usr/bin/env bash

#https://docs.travis-ci.com/user/environment-variables/#convenience-variables
#https://docs.travis-ci.com/user/deployment/script/

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

if [ "$TRAVIS_BRANCH" = "develop" ]; then
    echo "Deploy da imagem de desenvolvimento..."
    docker push marcelomaia/portal_uniforme_backend
fi

tag="$TRAVIS_TAG"
if [ -n "$tag" ]; then
    echo "Deploy da imagem de produção..."
    docker tag marcelomaia/portal_uniforme_backend:latest marcelomaia/portal_uniforme_backend:$tag
    docker push marcelomaia/portal_uniforme_backend:$tag
fi