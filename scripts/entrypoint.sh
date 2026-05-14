#!/bin/bash

# For use in development only.
# Installs in editable mode any libs mounted under /editable/
# This way, we can easily work on e.g. librarian.

for lib in /editable/*
do
    [ -d "$lib" ] || continue
    pip install -e $lib
done

exec "$@"
