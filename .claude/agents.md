# Regles d'utilisation des sous-agents

> Ce fichier definit quand Claude doit utiliser des sous-agents specialises.
> L'utilisateur n'a pas a s'en occuper - c'est automatique.

## Agents actifs

### 1. Architecture Reviewer
**Quand** : Apres avoir cree/modifie du code dans un module
**Role** : Verifier que Clean Architecture est respectee
**Checklist** :
- Domain n'importe pas de frameworks
- Use cases dependent d'interfaces (pas d'implementations)
- Pas d'import direct entre modules (sauf events)

### 2. Test Writer
**Quand** : Apres avoir cree un use case
**Role** : Generer les tests unitaires avec mocks
**Convention** : Fichier `test_{nom}.py` dans `tests/unit/{module}/`

### 3. Code Quality
**Quand** : Avant de committer
**Role** : Verifier docstrings, type hints, conventions de nommage

## Regles simples

1. **Un agent a la fois** - Jamais plusieurs en parallele
2. **Toujours finir** - Ne pas lancer un agent si le precedent n'a pas termine
3. **Resultats integres** - Je corrige moi-meme les problemes trouves
4. **Pas de bruit** - Je n'en parle a l'utilisateur que si c'est pertinent

## Quand NE PAS utiliser d'agent

- Questions simples
- Modifications mineures (< 20 lignes)
- Documentation seule
- Configuration/scripts
