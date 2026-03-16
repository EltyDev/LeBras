# Guide Complet d'Installation et Configuration - LeBras

Ce guide couvre l'ensemble du processus d'installation, configuration et utilisation du système de teleopération avec le robot SO-101.

## Table des matières

1. [Installation des dépendances](#installation-des-dépendances)
2. [Configuration du matériel](#configuration-du-matériel)
3. [Calibration des moteurs](#calibration-des-moteurs)
4. [Test de connexion](#test-de-connexion)
5. [Teleopération](#teleopération)
6. [Enregistrement de données](#enregistrement-de-données)
7. [Entraînement d'un modèle](#entraînement-dun-modèle)
8. [Exécution d'une policy](#exécution-dune-policy)
9. [Dépannage](#dépannage)

---

## Installation des dépendances

### Étape 1 : Installer Miniforge

Miniforge est une distribution légère de conda optimisée pour les environnements de conda-forge.

#### Sur Windows :
1. Téléchargez le dernier installateur depuis [ici](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe)
2. Exécutez l'installateur et suivez les instructions
3. Acceptez d'ajouter Miniforge à votre PATH lors de l'installation

#### Sur Linux :
```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

### Étape 2 : Créer et activer l'environnement Conda

Ouvrez un terminal (PowerShell ou Command Prompt sur Windows, Terminal sur Linux) et exécutez :

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

Vous devriez voir `(lerobot)` au début de votre ligne de commande, indiquant que l'environnement est activé.

### Étape 3 : Installer les dépendances

```bash
conda install ffmpeg -c conda-forge
pip install lerobot
```

### Étape 4 : Configuration CUDA optionnelle (recommandé)

Si vous avez une GPU Nvidia et souhaitez accélérer l'inférence, installez le support CUDA :

1. Téléchargez et installez [CUDA Toolkit 12.4](https://developer.nvidia.com/cuda-downloads)
2. Téléchargez et installez [cuDNN](https://developer.nvidia.com/cudnn)
3. Installez PyTorch avec support CUDA :

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

---

## Configuration du matériel

### Étape 1 : Identifier les ports COM

Sur Windows, le robot communique via des ports COM (COM3, COM4, COM5, COM6, etc.). Vous avez besoin de deux ports : un pour le leader et un pour le follower.

#### Trouver les ports :

```bash
lerobot-find-robot
```

Notez les numéros de port. Par exemple :
- Leader (téléopérateur) : `COM5`
- Follower (robot à contrôler) : `COM6`

### Étape 2 : Identifier la caméra

Si vous utilisez une caméra USB pour le feedback vidéo :

```bash
lerobot-find-camera
```

Notez l'index ou le chemin de la caméra. Exemple : index `1` pour une caméra USB.

### Étape 3 : Localiser les fichiers de calibration

Les fichiers de calibration actuels sont situés dans le dossier `calibration_files/` :
- `leader-1.json` : Configuration du robot leader (téléopérateur)
- `follower-1.json` : Configuration du robot follower (robot contrôlé)

---

## Calibration des moteurs

### Étape 1 : Vérifier le statut des moteurs

Avant de calibrer, assurez-vous que tous les moteurs sont bien connectés et alimentés. Connectez le robot et exécutez :

```bash
lerobot-setup-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1
```

Remplacez `COM6` par le vrai port de votre follower.

Vérifiez que :
- Tous les 6 moteurs sont détectés (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper)
- Les LEDs ne clignotent pas (sinon, problème de connexion)
- Le statut de chaque moteur est "OK"

### Étape 2 : Générer les fichiers de calibration

Si vous n'avez pas encore les fichiers de calibration ou si le robot a changé :

```bash
lerobot-calibrate-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --robot.calibration_dir=.
```

Cela créera un fichier `follower-1.json` avec les paramètres de calibration pour chaque moteur.

Répétez pour le leader si nécessaire :

```bash
lerobot-calibrate-motors --robot.type=so101_leader --robot.port=COM5 --robot.id=leader-1 --robot.calibration_dir=.
```

### Étape 3 : Vérifier les paramètres de calibration

Ouvrez les fichiers JSON de calibration (exemple `calibration_files/follower-1.json`) et vérifiez que chaque moteur a :
- `id` : Identifiant du moteur (1-6)
- `homing_offset` : Position de référence
- `range_min` et `range_max` : Limites de mouvement

Exemple de structure :
```json
{
    "shoulder_pan": {
        "id": 1,
        "drive_mode": 0,
        "homing_offset": 1618,
        "range_min": 769,
        "range_max": 3156
    },
    ...
}
```

### Étape 4 : Tester la calibration

Pour vérifier que la calibration est correcte, testez une connexion simple (voir section [Test de connexion](#test-de-connexion)).

---

## Test de connexion

### Étape 1 : Réinitialiser le robot (optionnel)

Si le robot est bloqué ou en position bizarre, réinitialisez-le avec le script fourni :

```bash
python scripts/reset.py
```

Entrez le port du robot quand demandé (ex: `COM6`). Cela désactivera le couple et ramènera le robot à une position neutre.

### Étape 2 : Tester la connexion du follower

```bash
python -c "
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

robot = SO101Follower(config=SO101FollowerConfig(
    port='COM6',
    id='follower-1'
))
robot.connect()
print('Robot follower connecté avec succès !')
print(f'État du robot: {robot}')
robot.disconnect()
"
```

Remplacez `COM6` par votre port réel.

### Étape 3 : Tester la connexion du leader

```bash
python -c "
from lerobot.robots.so_leader import SO101Leader, SO101LeaderConfig

robot = SO101Leader(config=SO101LeaderConfig(
    port='COM5',
    id='leader-1'
))
robot.connect()
print('Robot leader connecté avec succès !')
print(f'État du robot: {robot}')
robot.disconnect()
"
```

---

## Teleopération

### Étape 1 : Préparation

Assurez-vous que :
- L'environnement conda `lerobot` est activé
- Les deux robots (leader et follower) sont alimentés
- Les deux ports COM sont identifiés
- Les fichiers de calibration existent dans `calibration_files/`

### Étape 2 : Lancer la teleopération

#### Version simple (sans caméra) :

```bash
lerobot-teleoperate ^
  --robot.type=so101_follower ^
  --robot.port=COM6 ^
  --robot.id=follower-1 ^
  --teleop.id=leader-1 ^
  --teleop.type=so101_leader ^
  --teleop.port=COM5 ^
  --robot.calibration_dir="." ^
  --teleop.calibration_dir="."
```

#### Version avec caméra USB (Windows) :

```bash
lerobot-teleoperate ^
  --robot.type=so101_follower ^
  --robot.port=COM6 ^
  --robot.id=follower-1 ^
  --teleop.id=leader-1 ^
  --teleop.type=so101_leader ^
  --teleop.port=COM5 ^
  --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}" ^
  --display_data=true
```

### Étape 3 : Utiliser la teleopération

- Manipulez le robot **leader** pour contrôler le robot **follower**
- L'écran affichera le flux vidéo (s'il y a une caméra)
- Appuyez sur `Ctrl+C` pour arrêter

---

## Enregistrement de données

### Étape 1 : Préparation

Créez un dossier pour votre dataset :

```bash
mkdir datasets/votre_tache
```

### Étape 2 : Enregistrer des épisodes

Enregistrez 50 épisodes pour la tâche "Sort cubes" :

```bash
lerobot-record ^
  --robot.type=so101_follower ^
  --robot.port=COM6 ^
  --robot.id=follower-1 ^
  --robot.calibration_dir=. ^
  --teleop.port=COM5 ^
  --teleop.type=so101_leader ^
  --teleop.calibration_dir="." ^
  --teleop.id=leader-1 ^
  --dataset.repo_id="local/dataset" ^
  --dataset.num_episodes=50 ^
  --dataset.push_to_hub=false ^
  --dataset.single_task="Sort cubes" ^
  --display_data=true ^
  --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}"
```

**Paramètres clés** :
- `--dataset.num_episodes` : Nombre d'épisodes à enregistrer
- `--dataset.single_task` : Nom de la tâche
- `--dataset.repo_id` : Chemin du dataset local ou ID Hugging Face

### Étape 3 : Vérifier les données enregistrées

Le dataset est sauvegardé dans `datasets/`. Vous pouvez le visualiser avec :

```bash
python -c "
from lerobot.datasets import load_dataset
dataset = load_dataset('local/dataset')
print(f'Nombre d\'épisodes: {len(dataset)}')
print(f'Informations: {dataset.info}')
"
```

---

## Entraînement d'un modèle

### Étape 1 : Vérifier le dataset

```bash
python -c "
from lerobot.datasets import load_dataset
dataset = load_dataset('local/dataset')
print(f'Dataset: {dataset}')
"
```

### Étape 2 : Entraîner un modèle ACT

Le modèle ACT (Action Chunking with Transformers) est efficace pour ce type de tâche :

```bash
lerobot-train ^
  --dataset.repo_id="local/dataset" ^
  --policy.type=act ^
  --output_dir=outputs/train/act_cubes ^
  --job_name=act_cubes ^
  --policy.device=cuda ^
  --policy.repo_id=<VOTRE_USERNAME>/act_cubes
```

**Paramètres clés** :
- `--policy.type` : Type de policy (`act`, `diffusion`, etc.)
- `--policy.device` : `cuda` pour GPU, `cpu` pour CPU
- `--output_dir` : Dossier de sauvegarde des checkpoints
- `--job_name` : Nom du travail d'entraînement

### Étape 3 : Suivi du progrès

Les checkpoints sont sauvegardés dans `outputs/train/act_cubes/`. Vous pouvez suivre la perte d'entraînement en utilisant TensorBoard :

```bash
tensorboard --logdir=outputs/train/act_cubes
```

---

## Exécution d'une Policy

### Étape 1 : Charger un modèle entraîné

```bash
python -c "
from lerobot.policy import load_policy

policy = load_policy(
    policy_name_or_path='outputs/train/act_cubes/checkpoints/000000',
    map_location='cuda'  # ou 'cpu'
)
print(f'Policy chargée avec succès !')
print(f'Type: {policy}')
"
```

### Étape 2 : Exécuter la policy en boucle fermée

```bash
python -c "
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
from lerobot.policy import load_policy

# Charger la policy
policy = load_policy(
    policy_name_or_path='outputs/train/act_cubes/checkpoints/000000',
    map_location='cuda'
)

# Connecter le robot
robot = SO101Follower(config=SO101FollowerConfig(
    port='COM6',
    id='follower-1'
))
robot.connect()

# Exécuter la policy
for step in range(100):  # 100 étapes
    # Obtenir l'observation (état du robot + images)
    observation = robot.get_observation()
    
    # Prédire l'action
    with torch.no_grad():
        action = policy(observation)
    
    # Exécuter l'action
    robot.send_action(action)
    print(f'Étape {step}: action envoyée')

robot.disconnect()
print('Exécution terminée !')
"
```

### Étape 3 : Exécution avec affichage vidéo

Pour une exécution avec feedback vidéo en temps réel :

```bash
python scripts/run_policy.py \
  --policy_name_or_path=outputs/train/act_cubes/checkpoints/000000 \
  --robot.port=COM6 \
  --robot.id=follower-1 \
  --robot.calibration_dir=. \
  --num_episodes=5 \
  --display_data=true
```

### Étape 4 : Test de la policy ACT en mode Record Eval

Pour tester la policy ACT entraînée en mode évaluation lors de l'enregistrement :

```bash
lerobot-record ^
  --robot.type=so101_follower ^
  --robot.port=COM6 ^
  --robot.id=follower-1 ^
  --robot.calibration_dir=. ^
  --teleop.port=COM5 ^
  --teleop.type=so101_leader ^
  --teleop.calibration_dir="." ^
  --teleop.id=leader-1 ^
  --dataset.repo_id="local/eval" ^
  --dataset.num_episodes=5 ^
  --dataset.push_to_hub=false ^
  --dataset.single_task="Sort cubes" ^
  --display_data=true ^
  --policy.repo_id=outputs/train/act_cubes/checkpoints/000000 ^
  --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}"
```

**Paramètres clés** :
- `--dataset.repo_id="local/eval"` : Active le mode évaluation (teste la policy au lieu de faire juste de la teleopération)
- `--policy.repo_id` : Chemin vers le checkpoint du modèle ACT entraîné
- `--dataset.num_episodes` : Nombre d'épisodes de test
- `--display_data=true` : Affiche les prédictions de la policy en temps réel

Cela permettra de voir comment la policy se comporte sur le robot réel pendant l'enregistrement.

---

## Dépannage

### Les moteurs ne sont pas détectés

**Symptômes** : LED clignotante, moteurs manquants dans la config

**Solutions** :
1. Vérifiez les connexions USB et les câbles du robot
2. Essayez le commande setup moteurs :
   ```bash
   lerobot-setup-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1
   ```
3. Réinitialisez le robot :
   ```bash
   python scripts/reset.py
   ```

### Mauvais port COM identifié

**Symptômes** : Erreur "Port not found" ou "No robot detected"

**Solutions** :
```bash
lerobot-find-robot
```

Vérifiez aussi dans le Gestionnaire de périphériques Windows (Ports COM).

### La caméra ne fonctionne pas

**Symptômes** : Erreur "Camera not found"

**Solutions** :
```bash
lerobot-find-camera
```

Essayez différents index (0, 1, 2, etc.) dans la configuration.

### Erreur de calibration

**Symptômes** : Moteurs en dehors de la plage de mouvement

**Solutions** :
1. Vérifiez les paramètres dans le fichier JSON (homing_offset, range_min, range_max)
2. Recalibrez les moteurs :
   ```bash
   lerobot-calibrate-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --robot.calibration_dir=.
   ```

### L'entraînement est lent

**Solutions** :
1. Assurez-vous que CUDA est activé : `--policy.device=cuda`
2. Réduisez la taille du batch : `--training.batch_size=16`
3. Utilisez une GPU plus puissante

### La policy produit des mouvements bizarres

**Causes possibles** :
1. Dataset trop petit (besoin de plus d'épisodes)
2. Calibration incorrecte
3. Hyperparamètres d'entraînement mal ajustés

**Solutions** :
1. Enregistrez plus d'épisodes
2. Vérifiez la calibration
3. Expérimentez avec les hyperparamètres

---

## Commandes utiles

### Réinitialiser le robot
```bash
python scripts/reset.py
```

### Trouver le port du robot
```bash
lerobot-find-robot
```

### Trouver la caméra
```bash
lerobot-find-camera
```

### Setup des moteurs
```bash
lerobot-setup-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1
```

### Calibrer les moteurs
```bash
lerobot-calibrate-motors --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --robot.calibration_dir=.
```

### Teleopération
```bash
lerobot-teleoperate --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --teleop.id=leader-1 --teleop.type=so101_leader --teleop.port=COM5 --robot.calibration_dir="." --teleop.calibration_dir="."
```

### Enregistrement
```bash
lerobot-record --robot.type=so101_follower --robot.port=COM6 --robot.id=follower-1 --robot.calibration_dir=. --teleop.port=COM5 --teleop.type=so101_leader --teleop.calibration_dir="." --teleop.id=leader-1 --dataset.repo_id="local/dataset" --dataset.num_episodes=10 --dataset.push_to_hub=false --dataset.single_task="Ma tâche" --display_data=true --robot.cameras="{ front: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}"
```

### Entraînement
```bash
lerobot-train --dataset.repo_id="local/dataset" --policy.type=act --output_dir=outputs/train/act_dataset --job_name=act_dataset --policy.device=cuda --policy.repo_id=<USERNAME>/act_dataset
```

---

## Checklist complète

- [ ] Miniforge installé
- [ ] Environnement conda créé et activé
- [ ] LeRobot et dépendances installés
- [ ] Ports COM identifiés (leader et follower)
- [ ] Moteurs détectés et configurés
- [ ] Fichiers de calibration présents
- [ ] Connexion des robots testée
- [ ] Teleopération fonctionnelle
- [ ] Dataset enregistré
- [ ] Model entraîné
- [ ] Policy exécutée avec succès

---

## Support et ressources

- [Documentation LeRobot](https://github.com/huggingface/lerobot)
- Consultez [TROUBLESHOOTING.md](TROUBLESHOOTING.md) pour des problèmes spécifiques
- Consultez [README.md](README.md) pour les commandes rapides
