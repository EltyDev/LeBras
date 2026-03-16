# Dépannage et Résolution des Problèmes

Ce guide couvre les problèmes courants rencontrés lors de l'installation, la configuration et l'utilisation du système LeRobot SO-101.

## Table des matières

1. [Problèmes de moteurs](#problèmes-de-moteurs)
2. [Problèmes de caméra](#problèmes-de-caméra)
3. [Problèmes de connexion robot](#problèmes-de-connexion-robot)
4. [Problèmes de calibration](#problèmes-de-calibration)
5. [Problèmes de teleopération](#problèmes-de-teleopération)
6. [Problèmes d'entraînement](#problèmes-dentraînement)
7. [Problèmes de performance](#problèmes-de-performance)
8. [Erreurs de configuration](#erreurs-de-configuration)

---

## Problèmes de moteurs

### Moteurs manquants lors de la configuration / LED clignotante

**Symptômes** :
- Les moteurs n'apparaissent pas lors de la connexion
- La LED du robot clignote
- Erreur : "Motor not found" ou "LED flashing"

**Causes possibles** :
- Moteurs mal connectés au contrôleur
- Câbles endommagés ou mal branchés
- Moteurs en défaut d'alimentation
- Firmware du moteur corrompu

**Solutions** :

1. **Vérifiez les connexions physiques** :
   - Assurez-vous que tous les moteurs sont correctement branchés au bus CAN
   - Vérifiez que l'alimentation du robot est suffisante (vérifiez les ampères requis)
   - Testez chaque câble pour voir s'il n'y a pas de rupture

2. **Configurez les moteurs** :
   ```bash
   lerobot-setup-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1
   ```

3. **Réinitialisez les moteurs** :
   ```bash
   python scripts/reset.py
   ```
   Entrez le port du robot quand demandé.

4. **Si le problème persiste** :
   - Débranchez l'alimentation pendant 30 secondes
   - Rebranchez et réessayez
   - Vérifiez si les fichiers de calibration JSON sont corrects

---

### Moteur bloqué ou ne répond pas

**Symptômes** :
- Un moteur ne bouge pas quand on le contrôle
- Le moteur fait du bruit mais ne tourne pas
- Erreur : "Torque error" ou "Position error"

**Causes possibles** :
- Moteur surcharger (couple insuffisant)
- Moteur en limite de range
- Problème électronique du moteur

**Solutions** :

1. **Désactivez le couple et testez manuellement** :
   ```bash
   python scripts/reset.py
   ```

2. **Vérifiez la plage de mouvement** dans le fichier JSON :
   ```json
   {
       "nom_moteur": {
           "range_min": 769,      // Position minimale
           "range_max": 3156      // Position maximale
       }
   }
   ```

3. **Augmentez le couple maximal** (dans la configuration) :
   - Cherchez le paramètre `max_torque` ou `torque_limit`
   - Augmentez-le progressivement

4. **Testez le moteur individuellement** :
   ```bash
   python -c "
   from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
   
   robot = SO101Follower(config=SO101FollowerConfig(port='COM6', id='follower-1'))
   robot.connect()
   
   # Testez un moteur spécifique
   robot.bus.write_position('shoulder_pan', 2000)  # Milieu de la plage
   robot.disconnect()
   "
   ```

---

## Problèmes de caméra

### Caméra manquante ou non détectée

**Symptômes** :
- Erreur : "Camera not found"
- L'image affichée est noire
- Pas de flux vidéo

**Causes possibles** :
- Caméra non branchée ou mal reconnue
- Mauvais index de caméra
- Driver USB manquant

**Solutions** :

1. **Trouvez les caméras disponibles** :
   ```bash
   lerobot-find-camera
   ```

2. **Vérifiez les périphériques USB** :
   - Sur Windows : Ouvrez le Gestionnaire de périphériques
   - Cherchez dans "Caméras" ou "Lecteurs de CD/DVD"
   - Vérifiez qu'il n'y a pas de point d'exclamation (!) sur le périphérique

3. **Essayez différents index dans la commande** :
   ```bash
   lerobot-teleoperate \
     --robot.type=so101_follower \
     --robot.port=COM6 \
     --robot.id=follower-1 \
     --teleop.type=so101_leader \
     --teleop.port=COM5 \
     --teleop.id=leader-1 \
     --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}}" \
     --display_data=true
   ```
   Remplacez l'index : 0, 1, 2, etc.

4. **Mettez à jour les drivers USB** :
   - Téléchargez les derniers drivers pour votre caméra
   - Installez-les et redémarrez

5. **Testez avec OpenCV directement** :
   ```bash
   python -c "
   import cv2
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   print(f'Caméra trouvée: {ret}')
   print(f'Dimensions: {frame.shape}')
   cap.release()
   "
   ```

---

### Caméra très lente ou décalage vidéo

**Symptômes** :
- FPS très bas (< 5)
- Décalage entre le mouvement réel et la vidéo
- Lag vidéo important

**Causes possibles** :
- Résolution trop élevée
- CPU surchargé
- Câble USB de mauvaise qualité

**Solutions** :

1. **Réduisez la résolution** :
   ```bash
   --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 320, height: 240, fps: 15}}"
   ```

2. **Réduisez le FPS** :
   ```bash
   --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 15}}"
   ```

3. **Fermez les applications gourmandes** :
   - Arrêtez les applications inutiles
   - Vérifiez l'utilisation CPU (Ctrl+Shift+Esc)

4. **Utilisez un câble USB 3.0** de bonne qualité

---

## Problèmes de connexion robot

### Robot manquant / Port COM introuvable

**Symptômes** :
- Erreur : "Port not found"
- Erreur : "Connection refused"
- "Device not found"

**Causes possibles** :
- Robot non branché ou mal reconnu
- Mauvais port COM spécifié
- Driver USB du robot manquant

**Solutions** :

1. **Trouvez automatiquement le robot** :
   ```bash
   lerobot-find-robot
   ```

2. **Vérifiez dans le Gestionnaire de périphériques** (Windows) :
   - Appuyez sur `Win + X` → "Gestionnaire de périphériques"
   - Expandez "Ports (COM et LPT)"
   - Notez les ports disponibles (ex: COM5, COM6)

3. **Vérifiez les câbles USB** :
   - Assurez-vous que le câble USB est bien branché
   - Testez un autre câble USB

4. **Mettez à jour les drivers** :
   - Téléchargez les derniers drivers USB pour le robot SO-101
   - Installez-les et redémarrez

5. **Réessayez avec un autre port USB** :
   - Si le robot était en COM6, branchez-le en COM3 et retentez
   - Parfois les ports USB ont des problèmes

6. **Testez avec un autre PC** pour vérifier que le robot n'est pas défectueux

---

### Port COM incorrect détecté

**Symptômes** :
- Plusieurs ports COM trouvés, difficile de savoir lequel est lequel
- Mauvais robot détecté après la reconnexion

**Solutions** :

1. **Identifiez les robots manuellement** :
   ```bash
   # Déconnectez le follower
   lerobot-find-robot
   # Note le port A
   
   # Reconnectez le follower, déconnectez le leader
   lerobot-find-robot
   # Note le port B
   ```

2. **Créez un script de détection** :
   ```bash
   python -c "
   from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
   
   for port in ['COM3', 'COM4', 'COM5', 'COM6']:
       try:
           robot = SO101Follower(config=SO101FollowerConfig(port=port, id='test'))
           robot.connect()
           print(f'Robot détecté en {port}')
           robot.disconnect()
       except Exception as e:
           print(f'Pas de robot en {port}')
   "
   ```

---

### Connexion établie mais robot non réactif

**Symptômes** :
- Connexion OK mais les moteurs ne répondent pas
- Erreur lors de l'envoi d'une commande

**Causes possibles** :
- Robot en mode verrouillé
- Couple désactivé
- Problème de calibration

**Solutions** :

1. **Réactivez le couple** :
   ```bash
   python -c "
   from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
   
   robot = SO101Follower(config=SO101FollowerConfig(port='COM6', id='follower-1'))
   robot.connect()
   robot.bus.enable_torque()
   print('Couple activé')
   robot.disconnect()
   "
   ```

2. **Vérifiez que la calibration est correcte** :
   - Assurez-vous que les fichiers `.json` existent dans `calibration_files/`
   - Vérifiez que le chemin passé à `--robot.calibration_dir="."` est correct

---

## Problèmes de calibration

### Moteur en dehors de sa plage de mouvement

**Symptômes** :
- Erreur : "Joint limit exceeded"
- Le moteur se bloque ou fait du bruit
- Position impossible à atteindre

**Causes possibles** :
- Paramètres `range_min` ou `range_max` incorrects
- Robot physiquement désaligné
- Calibration mal faite

**Solutions** :

1. **Recalibrez les moteurs** :
   ```bash
   lerobot-calibrate-motors \
     --robot.type=so101_follower \
     --robot.port=COM6 \
     --robot.id=follower-1 \
     --robot.calibration_dir=.
   ```

2. **Vérifiez les valeurs de calibration** :
   Ouvrez `calibration_files/follower-1.json` et vérifiez :
   ```json
   {
       "shoulder_pan": {
           "homing_offset": 1618,  // Doit être entre range_min et range_max
           "range_min": 769,
           "range_max": 3156
       }
   }
   ```

3. **Vérifiez l'alignement physique** :
   - Assurez-vous que tous les moteurs sont bien serrés
   - Vérifiez que rien n'obstrue le mouvement

---

### Homing_offset incorrect

**Symptômes** :
- Robot en position étrange après démarrage
- Le robot se "cale" à la position de démarrage

**Causes possibles** :
- Calibration faite quand le robot était en position incorrecte
- Moteur bougeait lors de la calibration

**Solutions** :

1. **Mettez le robot en position neutre** :
   ```bash
   python scripts/reset.py
   ```

2. **Recalibrez** :
   ```bash
   lerobot-calibrate-motors \
     --robot.type=so101_follower \
     --robot.port=COM6 \
     --robot.id=follower-1 \
     --robot.calibration_dir=.
   ```

---

## Problèmes de teleopération

### Teleopération ne démarre pas

**Symptômes** :
- Erreur au lancement de `lerobot-teleoperate`
- "Failed to connect to robots"

**Causes possibles** :
- Ports incorrects
- Robots non calibrés
- Fichiers de calibration manquants

**Solutions** :

1. **Vérifiez les ports** :
   ```bash
   lerobot-find-robot
   ```

2. **Vérifiez que les fichiers de calibration existent** :
   ```bash
   ls calibration_files/
   # Doit afficher : follower-1.json, leader-1.json
   ```

3. **Testez la connexion de chaque robot individuellement** :
   ```bash
   python -c "
   from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
   robot = SO101Follower(config=SO101FollowerConfig(port='COM6', id='follower-1'))
   robot.connect()
   print('Follower OK')
   robot.disconnect()
   "
   
   python -c "
   from lerobot.robots.so101_leader import SO101Leader, SO101LeaderConfig
   robot = SO101Leader(config=SO101LeaderConfig(port='COM5', id='leader-1'))
   robot.connect()
   print('Leader OK')
   robot.disconnect()
   "
   ```

---

### Leader et Follower ne se synchronisent pas

**Symptômes** :
- Le follower ne suit pas les mouvements du leader
- Délai important entre le mouvement du leader et du follower
- Follower se déplace bizarrement

**Causes possibles** :
- Calibration différente entre leader et follower
- Problème de lag de communication
- Moteurs avec couples différents

**Solutions** :

1. **Vérifiez que les calibrations sont correctes** :
   ```bash
   # Pour le follower
   lerobot-calibrate-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --robot.calibration_dir=.
   
   # Pour le leader
   lerobot-calibrate-motors --robot.type=so101_leader --robot.port=COM5 --robot.id=leader-1 --robot.calibration_dir=.
   ```

2. **Vérifiez la synchronisation temporelle** :
   - Testez avec une tâche simple (bouger un seul moteur)
   - Notez le délai

3. **Réduisez la vitesse** :
   Ajoutez dans la commande (si supporté) :
   ```bash
   --policy.execute_every_n_steps=2  # Réduit la fréquence d'exécution
   ```

---

## Problèmes d'entraînement

### Entraînement se lance très lentement

**Symptômes** :
- Prend longtemps à démarrer
- Utilisation GPU à 0%

**Causes possibles** :
- CUDA non détecté
- Mauvaise version de PyTorch
- GPU non utilisé

**Solutions** :

1. **Vérifiez que CUDA est détecté** :
   ```bash
   python -c "
   import torch
   print(f'CUDA disponible: {torch.cuda.is_available()}')
   print(f'GPU: {torch.cuda.get_device_name(0)}')
   "
   ```

2. **Si CUDA n'est pas disponible, réinstallez PyTorch** :
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

3. **Assurez-vous que le paramètre est correct** :
   ```bash
   --policy.device=cuda
   ```

---

### Entraînement s'arrête / Out of Memory (OOM)

**Symptômes** :
- Erreur : "CUDA out of memory"
- Processus d'entraînement tue brutalement

**Causes possibles** :
- Batch size trop élevé
- Modèle trop gros pour la GPU
- Autres applications utilisant la mémoire GPU

**Solutions** :

1. **Réduisez la taille du batch** :
   ```bash
   --training.batch_size=8
   ```

2. **Réduisez la longueur des séquences** :
   ```bash
   --policy.chunk_size=32
   ```

3. **Fermez les autres applications** utilisant la GPU
   ```bash
   # Sur Windows, vérifiez GPU-Z ou nvidia-smi
   nvidia-smi
   ```

4. **Utilisez le CPU si nécessaire** (plus lent) :
   ```bash
   --policy.device=cpu
   ```

---

### La loss d'entraînement ne diminue pas

**Symptômes** :
- Loss reste constante ou augmente
- Model ne converge pas

**Causes possibles** :
- Learning rate trop élevé ou trop bas
- Dataset insuffisant
- Dataset non mélangé correctement

**Solutions** :

1. **Ajustez le learning rate** :
   ```bash
   --training.learning_rate=1e-4  # Essayez différentes valeurs
   ```

2. **Augmentez la quantité de données** :
   - Enregistrez plus d'épisodes
   ```bash
   --dataset.num_episodes=50  # Plus que 10
   ```

3. **Visualisez les données d'entraînement** :
   ```bash
   python -c "
   from lerobot.datasets import load_dataset
   dataset = load_dataset('local/dataset')
   print(f'Episodes: {len(dataset)}')
   print(f'Total frames: {sum(len(ep) for ep in dataset)}')
   "
   ```

---

## Problèmes de performance

### Le système est très lent

**Causes possibles** :
- CPU/GPU surchargé
- Trop de processus en arrière-plan
- Disque SSD lent

**Solutions** :

1. **Vérifiez l'utilisation des ressources** :
   - Ouvrez Gestionnaire des tâches (Ctrl+Shift+Esc)
   - Cherchez les processus gourmands

2. **Fermez les applications inutiles** :
   - Navigateurs web
   - Editeurs vidéo
   - Autres applications lourdes

3. **Vérifiez l'espace disque** :
   ```bash
   # Sur Windows
   Get-Volume
   ```

---

## Erreurs de configuration

### Erreur de import : "ModuleNotFoundError: No module named 'lerobot'"

**Symptômes** :
```
ModuleNotFoundError: No module named 'lerobot'
```

**Cause** :
- LeRobot n'est pas installé ou mauvais environnement conda

**Solution** :

1. **Vérifiez que vous êtes dans l'environnement `lerobot`** :
   ```bash
   conda activate lerobot
   ```

2. **Réinstallez LeRobot** :
   ```bash
   pip install lerobot
   ```

---

### Erreur de syntaxe : "SyntaxError"

**Symptômes** :
```
SyntaxError: invalid syntax
```

**Causes possibles** :
- Mauvaise version de Python
- Caractères spéciaux dans le chemin
- Guillemets mal échappés

**Solutions** :

1. **Vérifiez la version de Python** :
   ```bash
   python --version
   # Doit être Python 3.12
   ```

2. **Échappez les guillemets correctement** :
   - Sur Windows (PowerShell) : Utilisez des simples quotes `'`
   - Sur Windows (Command Prompt) : Utilisez `"`

---

## Ressources utiles

- [Documentation LeRobot officielle](https://github.com/huggingface/lerobot)
- [Issues GitHub LeRobot](https://github.com/huggingface/lerobot/issues)

---

## Besoin d'aide supplémentaire ?

Si vous avez toujours des problèmes :

1. Vérifiez que tous les drivers sont à jour
2. Consultez les logs complets (ajoutez `--debug` aux commandes)
3. Testez sur un autre PC si possible
4. Ouvrez une issue sur GitHub avec les détails du problème
