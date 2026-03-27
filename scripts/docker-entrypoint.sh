#!/usr/bin/env bash

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Set IFS to prevent word splitting issues
IFS=$'\n\t'

# Script metadata
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_warn() {
    echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Error handler
error_handler() {
    local line_number=$1
    log_error "Script failed at line ${line_number}"
    exit 1
}

trap 'error_handler ${LINENO}' ERR

# Graceful shutdown handler
shutdown_handler() {
    log_info "Received shutdown signal, cleaning up..."
    # Perform any cleanup operations here
    exit 0
}

trap shutdown_handler SIGTERM SIGINT

# Validate required environment variables
validate_environment() {
    log_info "Validating environment variables..."

    local required_vars=(
        "DATABASE_URL"
    )

    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi

    log_info "Environment validation passed"
    return 0
}

# Wait for database to be ready
wait_for_database() {
    log_info "Waiting for database to be ready..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if python -c "
import sys
from prisma import Prisma

try:
    db = Prisma()
    db.connect()
    db.disconnect()
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
            log_info "Database is ready"
            return 0
        fi

        log_warn "Database not ready, attempt ${attempt}/${max_attempts}"
        sleep 2
        ((attempt++))
    done

    log_error "Database did not become ready after ${max_attempts} attempts"
    return 1
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    if ! prisma migrate deploy; then
        log_error "Database migration failed"
        return 1
    fi

    log_info "Database migrations completed successfully"
    return 0
}

# Generate Prisma Client
generate_prisma_client() {
    log_info "Generating Prisma Client..."

    if ! prisma generate; then
        log_error "Prisma Client generation failed"
        return 1
    fi

    log_info "Prisma Client generated successfully"
    return 0
}

# Main execution
main() {
    log_info "Starting ${SCRIPT_NAME}..."
    log_info "Environment: ${ENVIRONMENT:-production}"

    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed"
        exit 1
    fi

    # Generate Prisma Client
    if ! generate_prisma_client; then
        log_error "Failed to generate Prisma Client"
        exit 1
    fi

    # Wait for database
    if ! wait_for_database; then
        log_error "Database is not available"
        exit 1
    fi

    # Run migrations
    if ! run_migrations; then
        log_error "Migration failed"
        exit 1
    fi

    log_info "Initialization completed successfully"
    log_info "Starting application: $*"

    # Execute the main command
    exec "$@"
}

# Run main function with all arguments
main "$@"
