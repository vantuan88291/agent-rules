#!/bin/bash
# Setup symlinks for all React Native projects

WORKSPACE_DIR="/home/vantuan88291/.openclaw/workspace/dev4"
SOURCE_DIR="/home/vantuan88291/Documents/code/reactnative"
TARGET_DIR="$WORKSPACE_DIR/reactnative"

echo "Setting up symlinks for React Native projects..."
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Create target directory if not exists
mkdir -p "$TARGET_DIR"

# Remove broken symlinks first
find "$TARGET_DIR" -maxdepth 1 -type l ! -exec test -e {} \; -delete 2>/dev/null

# Loop through all directories in source and create symlinks
for project in "$SOURCE_DIR"/*; do
    if [ -d "$project" ]; then
        project_name=$(basename "$project")
        symlink_path="$TARGET_DIR/$project_name"
        
        # Remove existing symlink or directory
        if [ -L "$symlink_path" ] || [ -e "$symlink_path" ]; then
            rm -rf "$symlink_path"
            echo "Removed existing: $project_name"
        fi
        
        # Create new symlink
        ln -s "$project" "$symlink_path"
        echo "Created symlink: $project_name -> $project"
    fi
done

echo ""
echo "Done! Projects linked:"
ls -la "$TARGET_DIR/"
