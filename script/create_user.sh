#!/bin/bash
set -e
set -o pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SHARED_VOLUME="shared_data"
REGISTRY_FILE="container_registry.json"
REGISTRY_LOCK="container_registry.lock"
BASE_URL="ey-ios.com"
NETWORK_NAME="user_shared_network"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKERFILE="$SCRIPT_DIR/Dockerfile"
SEED_DATA_PRIVATE="$PARENT_DIR/data_private"
SEED_DATA_SHARED="$PARENT_DIR/data_shared"

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

validate_name() {
    [[ ! "$1" =~ ^[a-zA-Z0-9_-]+$ ]] && { print_error "Invalid name. Use alphanumeric, hyphens, underscores only."; exit 1; }
}

usage() {
    echo "Usage: $0 <container_name> <user_tag>"
    echo "Example: $0 user_alice development"
    exit 1
}

[ $# -ne 2 ] && { print_error "Invalid arguments"; usage; }

CONTAINER_NAME="$1"
USER_TAG="$2"
validate_name "$CONTAINER_NAME"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PRIVATE_VOLUME="${CONTAINER_NAME}_private"

# Build custom image if Dockerfile exists
if [ -f "$DOCKERFILE" ]; then
    print_info "Building custom image..."
    CUSTOM_IMAGE="user_base:latest"
    docker build -t "$CUSTOM_IMAGE" -f "$DOCKERFILE" "$SCRIPT_DIR" >/dev/null 2>&1
    IMAGE="$CUSTOM_IMAGE"
else
    IMAGE="ubuntu:latest"
fi

# Create network if needed
docker network inspect "$NETWORK_NAME" &>/dev/null || {
    print_info "Creating network: $NETWORK_NAME"
    docker network create "$NETWORK_NAME" >/dev/null
}

# Create shared volume if needed
docker volume inspect "$SHARED_VOLUME" &>/dev/null || {
    print_info "Creating shared volume: $SHARED_VOLUME"
    docker volume create "$SHARED_VOLUME" >/dev/null
}

# Handle private volume
if docker volume inspect "$PRIVATE_VOLUME" &>/dev/null; then
    print_warning "Volume '$PRIVATE_VOLUME' exists. Recreate? (yes/no): "
    read -r confirm
    [ "$confirm" = "yes" ] && docker volume rm "$PRIVATE_VOLUME" >/dev/null
fi
docker volume create "$PRIVATE_VOLUME" >/dev/null 2>&1 || true

# Seed private volume
if [ -d "$SEED_DATA_PRIVATE" ]; then
    print_info "Seeding private volume from: $SEED_DATA_PRIVATE"
    docker run --rm \
        -v "$PRIVATE_VOLUME:/mnt/target" \
        -v "$SEED_DATA_PRIVATE:/mnt/source:ro" \
        ubuntu:latest \
        bash -c "cp -r /mnt/source/. /mnt/target/ 2>/dev/null || true; chown -R 1000:1000 /mnt/target" >/dev/null 2>&1
    print_success "Private data seeded"
else
    print_warning "Private data directory not found: $SEED_DATA_PRIVATE"
fi

# Seed shared volume (once)
if [ -d "$SEED_DATA_SHARED" ]; then
    IS_EMPTY=$(docker run --rm -v "$SHARED_VOLUME:/mnt" ubuntu:latest bash -c "[ -z \"\$(ls -A /mnt 2>/dev/null)\" ] && echo 'yes' || echo 'no'")
    if [ "$IS_EMPTY" = "yes" ]; then
        print_info "Seeding shared volume from: $SEED_DATA_SHARED"
        docker run --rm \
            -v "$SHARED_VOLUME:/mnt/target" \
            -v "$SEED_DATA_SHARED:/mnt/source:ro" \
            ubuntu:latest \
            bash -c "cp -r /mnt/source/. /mnt/target/ 2>/dev/null || true; chown -R 1000:1000 /mnt/target" >/dev/null 2>&1
        print_success "Shared data seeded"
    else
        print_info "Shared volume already contains data, skipping seed"
    fi
else
    print_warning "Shared data directory not found: $SEED_DATA_SHARED"
fi

# Initialize registry in shared volume
print_info "Initializing registry..."
docker run --rm \
    -v "$SHARED_VOLUME:/mnt/shared" \
    ubuntu:latest \
    bash -c "
        mkdir -p /mnt/shared
        if [ ! -f /mnt/shared/$REGISTRY_FILE ]; then
            echo '[]' > /mnt/shared/$REGISTRY_FILE
            chmod 666 /mnt/shared/$REGISTRY_FILE
        fi
    " >/dev/null 2>&1

# Remove existing container if present
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_warning "Container '$CONTAINER_NAME' exists. Remove? (yes/no): "
    read -r confirm
    [ "$confirm" != "yes" ] && { print_error "Aborted"; exit 1; }
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
fi

# Create container
print_info "Creating container with image: $IMAGE"
docker run -d \
    --name "$CONTAINER_NAME" \
    --hostname "$CONTAINER_NAME" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    --label "user_tag=$USER_TAG" \
    --label "created=$TIMESTAMP" \
    -v "$PRIVATE_VOLUME:/app/private" \
    -v "$SHARED_VOLUME:/app/shared:rw" \
    -w /app/private \
    -e "CONTAINER_NAME=$CONTAINER_NAME" \
    -e "TAGS=$USER_TAG" \
    -e "PRIVATE_DATA_PATH=/app/private" \
    -e "SHARED_DATA_PATH=/app/shared" \
    "$IMAGE" \
    sleep infinity

# Wait and verify
sleep 2
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Container failed to start"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -20
    exit 1
fi
print_success "Container running"

# Register in shared volume registry
print_info "Registering container in shared registry..."
docker exec "$CONTAINER_NAME" bash -c "
    apt-get update -qq && apt-get install -y -qq jq >/dev/null 2>&1
    
    REGISTRY='/app/shared/$REGISTRY_FILE'
    LOCKFILE='/app/shared/$REGISTRY_LOCK'
    
    # Acquire lock
    RETRIES=0
    while ! mkdir \"\$LOCKFILE\" 2>/dev/null; do
        sleep 0.1
        RETRIES=\$((RETRIES + 1))
        [ \$RETRIES -gt 50 ] && { echo 'Lock timeout'; exit 1; }
    done
    trap 'rmdir \"\$LOCKFILE\" 2>/dev/null || true' EXIT
    
    # Add entry
    NEW_ENTRY='{\"container_name\":\"$CONTAINER_NAME\",\"user_tag\":\"$USER_TAG\",\"created\":\"$TIMESTAMP\"}'
    jq --argjson entry \"\$NEW_ENTRY\" '. += [\$entry]' \"\$REGISTRY\" > /tmp/registry_new.json
    mv /tmp/registry_new.json \"\$REGISTRY\"
    chmod 666 \"\$REGISTRY\"
" >/dev/null 2>&1

print_success "Container registered in shared registry"

# Display info
echo ""
echo "=============================================="
print_success "DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "📦 Container: $CONTAINER_NAME"
echo "🏷️  User Tag: $USER_TAG"
echo "⏰ Created: $TIMESTAMP"
echo "🖼️  Image: $IMAGE"
echo ""
echo "💡 Quick Commands:"
echo "   docker exec -it $CONTAINER_NAME bash"
echo "   docker logs -f $CONTAINER_NAME"
echo "   docker stop $CONTAINER_NAME"
echo "   docker start $CONTAINER_NAME"
echo ""
echo "📂 Volumes:"
echo "   Private: $PRIVATE_VOLUME → /app/private (RW)"
echo "   Shared:  $SHARED_VOLUME → /app/shared (RW)"
echo ""
echo "📋 Registry:"
echo "   docker exec $CONTAINER_NAME cat /app/shared/$REGISTRY_FILE | jq"
echo ""
echo "🔍 Labels:"
echo "   docker inspect $CONTAINER_NAME --format '{{json .Config.Labels}}' | jq"
echo ""
echo "🌐 Network: $NETWORK_NAME"
echo ""
echo "=============================================="