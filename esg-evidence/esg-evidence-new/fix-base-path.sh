#!/bin/bash
# Fix absolute paths in Evidence build for GitHub Pages base path
# Based on workaround from https://github.com/evidence-dev/evidence/issues/603

BASE_PATH="/esg-carbon-tracker"
BUILD_DIR="build"

echo "Fixing absolute paths to include base path: $BASE_PATH"

# Fix href and src attributes in HTML and JS files
# Use sed syntax that works on both Linux and macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  find "$BUILD_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i '' \
    -e "s|href=\"/\([^\"]*\)\"|href=\"$BASE_PATH/\1\"|g" \
    -e "s|src=\"/\([^\"]*\)\"|src=\"$BASE_PATH/\1\"|g" \
    -e "s|\"url\":\"/|\"url\":\"$BASE_PATH/|g" \
    -e "s|data-url=\"/|data-url=\"$BASE_PATH/|g" \
    {} +
else
  # Linux
  find "$BUILD_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i \
    -e "s|href=\"/\([^\"]*\)\"|href=\"$BASE_PATH/\1\"|g" \
    -e "s|src=\"/\([^\"]*\)\"|src=\"$BASE_PATH/\1\"|g" \
    -e "s|\"url\":\"/|\"url\":\"$BASE_PATH/|g" \
    -e "s|data-url=\"/|data-url=\"$BASE_PATH/|g" \
    {} +
fi

echo "Path fix complete!"
