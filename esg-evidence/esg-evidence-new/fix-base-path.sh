#!/bin/bash
# Fix absolute paths in Evidence build for GitHub Pages base path
# Based on workaround from https://github.com/evidence-dev/evidence/issues/603

BASE_PATH="/esg-carbon-tracker"
BUILD_DIR="build"

echo "Fixing absolute paths to include base path: $BASE_PATH"

# Fix paths in HTML and JS files
# Match: href="/...", src="/...", "url":"/...", '/...'
# Skip: already prefixed paths, protocol-relative URLs (//), http(s)://
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  find "$BUILD_DIR" -type f \( -name "*.js" -o -name "*.html" -o -name "*.json" \) -exec sed -i '' \
    -e "s|=\"/\([^/\"]\)|=\"$BASE_PATH/\1|g" \
    -e "s|:\"/\([^/\"]\)|:\"$BASE_PATH/\1|g" \
    -e "s|,\"/\([^/\"]\)|,\"$BASE_PATH/\1|g" \
    {} +
else
  # Linux
  find "$BUILD_DIR" -type f \( -name "*.js" -o -name "*.html" -o -name "*.json" \) -exec sed -i \
    -e "s|=\"/\([^/\"]\)|=\"$BASE_PATH/\1|g" \
    -e "s|:\"/\([^/\"]\)|:\"$BASE_PATH/\1|g" \
    -e "s|,\"/\([^/\"]\)|,\"$BASE_PATH/\1|g" \
    {} +
fi

echo "Path fix complete!"
