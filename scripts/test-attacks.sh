#!/bin/bash

# Couleurs pour le formatage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
TARGET="172.18.0.2"

# Fonction pour attendre entre les tests
wait_test() {
    echo -e "${YELLOW}Attente de 5 secondes...${NC}"
    sleep 5
    echo "-----------------------------------"
}

# Fonction pour les tests individuels
test_simple_connection() {
    echo -e "${GREEN}Test: Tentative de connexion simple${NC}"
    docker exec attacker hydra -l root -p wrongpass -t 1 $TARGET ssh
    wait_test
}

test_invalid_user() {
    echo -e "${GREEN}Test: Tentative avec utilisateur invalide${NC}"
    docker exec attacker hydra -l fakeuser -p password -t 1 $TARGET ssh
    wait_test
}

test_root_connection() {
    echo -e "${GREEN}Test: Tentative de connexion root${NC}"
    docker exec attacker hydra -l root -p wrongpass -t 1 $TARGET ssh
    wait_test
}

test_brute_force() {
    echo -e "${GREEN}Test: Simulation brute force${NC}"
    # Créer une petite liste de mots de passe pour le test
    docker exec attacker bash -c 'echo -e "wrongpass1\nwrongpass2\nwrongpass3\nwrongpass4\nwrongpass5" > /tmp/passlist.txt'
    docker exec attacker hydra -l root -P /tmp/passlist.txt -t 4 $TARGET ssh
    wait_test
}

test_port_scan() {
    echo -e "${GREEN}Test: Scan de port SSH${NC}"
    docker exec attacker nmap -p22 -sS $TARGET
    wait_test
}

test_ssh_version() {
    echo -e "${GREEN}Test: Vérification version SSH${NC}"
    docker exec attacker nmap -p22 -sV $TARGET
    wait_test
}

test_successful_login() {
    echo -e "${GREEN}Test: Connexion réussie${NC}"
    docker exec attacker hydra -l root -p password -t 1 $TARGET ssh
    wait_test
}

# Menu principal
show_menu() {
    echo -e "\n${GREEN}=== Menu de Tests d'Attaques SSH ===${NC}"
    echo "1. Exécuter tous les tests"
    echo "2. Test de connexion simple (mauvais mot de passe)"
    echo "3. Test avec utilisateur invalide"
    echo "4. Test de connexion root"
    echo "5. Test de force brute"
    echo "6. Scan de port SSH"
    echo "7. Vérification version SSH"
    echo "8. Test de connexion réussie"
    echo "q. Quitter"
    echo -n "Choix: "
}

# Fonction pour exécuter tous les tests
run_all_tests() {
    test_simple_connection
    test_invalid_user
    test_root_connection
    test_brute_force
    test_port_scan
    test_ssh_version
    test_successful_login
}

# Boucle principale
while true; do
    show_menu
    read choice

    case $choice in
        1)
            run_all_tests
            ;;
        2)
            test_simple_connection
            ;;
        3)
            test_invalid_user
            ;;
        4)
            test_root_connection
            ;;
        5)
            test_brute_force
            ;;
        6)
            test_port_scan
            ;;
        7)
            test_ssh_version
            ;;
        8)
            test_successful_login
            ;;
        q)
            echo -e "${GREEN}Au revoir!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Option invalide${NC}"
            ;;
    esac
done 