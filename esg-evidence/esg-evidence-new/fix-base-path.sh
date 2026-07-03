#!/bin/bash
# Fix absolute paths in Evidence build for GitHub Pages base path
# Based on workaround from https://github.com/evidence-dev/evidence/issues/603

BASE_PATH="/esg-carbon-tracker"
BUILD_DIR="build"

echo "Fixing absolute paths to include base path: $BASE_PATH"

# Fix href and src attributes in HTML and JS files
find "$BUILD_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i '' \
  -e "s|href=\"/\([^\"]*\)\"|href=\"$BASE_PATH/\1\"|g" \
  -e "s|src=\"/\([^\"]*\)\"|src=\"$BASE_PATH/\1\"|g" \
  -e "s|\"url\":\"/|\"url\":\"$BASE_PATH/|g" \
  -e "s|data-url=\"/|data-url=\"$BASE_PATH/|g" \
  {} +

echo "Path fix complete!"
