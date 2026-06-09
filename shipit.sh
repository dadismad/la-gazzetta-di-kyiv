#!/bin/bash
# Wrapper — runs shipit.sh from workdir (project root)
cd ~/projects/gazzetta-di-kyiv && exec bash shipit.sh "$@"
