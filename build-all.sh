#!/bin/bash

IMAGE=jmc265/docker-events-pushbullet
VERSION=$(git describe --exact-match --tags HEAD 2>/dev/null)
if ! VERSION="$(git describe --exact-match --tags HEAD 2>/dev/null)"; then
  echo "Current commit doesn't have a release tag. Won't build."
  echo "Please check: https://git-scm.com/book/en/v2/Git-Basics-Tagging"
  exit 1
fi

echo "Building ${IMAGE}:${VERSION}"
docker build --build-arg BUILD_VERSION="${VERSION}" -t "${IMAGE}:${VERSION}" .

echo "Pushing ${IMAGE}:${VERSION}"
docker push "${IMAGE}:${VERSION}"
