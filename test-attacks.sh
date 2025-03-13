#!/bin/bash

# Fonction pour attendre entre les tests
wait_test() {
    echo "Attente de 5 secondes..."
    sleep 5
    echo "-----------------------------------"
}

# Test 1: Tentative de connexion simple
echo "Test 1: Tentative de connexion simple"
docker exec attacker sshpass -p "wrongpass" ssh -o StrictHostKeyChecking=no root@172.18.0.2
wait_test

# Test 2: Utilisateur invalide
echo "Test 2: Tentative avec utilisateur invalide"
docker exec attacker sshpass -p "password" ssh -o StrictHostKeyChecking=no fakeuser@172.18.0.2
wait_test

# Test 3: Tentative de connexion root
echo "Test 3: Tentative de connexion root"
docker exec attacker sshpass -p "wrongpass" ssh -o StrictHostKeyChecking=no root@172.18.0.2
wait_test

# Test 4: Multiple tentatives (brute force)
echo "Test 4: Simulation brute force"
for i in {1..5}; do
    docker exec attacker sshpass -p "wrongpass$i" ssh -o StrictHostKeyChecking=no root@172.18.0.2
    sleep 1
done
wait_test

# Test 5: Scan de port
echo "Test 5: Scan de port SSH"
docker exec attacker nmap -p22 -sS 172.18.0.2
wait_test

# Test 6: Version SSH
echo "Test 6: Vérification version SSH"
docker exec attacker nc -vz 172.18.0.2 22
wait_test

# Test 7: Connexion réussie
echo "Test 7: Connexion réussie"
docker exec attacker sshpass -p "password" ssh -o StrictHostKeyChecking=no root@172.18.0.2 "echo 'Connexion réussie'"
wait_test 