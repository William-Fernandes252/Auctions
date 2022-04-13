#!/bin/bash

set -o errexit
set -o nounset

celery -A commerce worker -l INFO