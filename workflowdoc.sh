#!/usr/bin/env bash

main() {

    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
    readonly SCRIPT_DIR

    if ! command -v docker &>/dev/null; then
        echo "Docker is required to run this script."
        echo "If you don't want to use Docker, you may run ./workflowdoc.py directly."
        exit 1
    fi

    echo "Building container image..."
    docker build --quiet -t workflowdoc "${SCRIPT_DIR}"
    echo
    echo

    echo "Running ./workflowdoc.py in container..."
    echo
    docker run --rm --volume "$(pwd):/workspace" workflowdoc "$@"
}

(
    set -euo pipefail
    main "$@"
)
