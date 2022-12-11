#!/usr/bin/bash

pattern='SC_\w+Loader'
echo "from .loaders.base import SC_LoaderBase"
for fn in *.py; do
    result="$(grep -P "class $pattern" "$fn")"
    if [ -n "$result" ]; then
        echo "from .loaders.${fn%.*} import $(echo "$result" | sed -E "s/.*($pattern).*/\\1/")"
    fi
done
