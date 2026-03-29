# Pygit

Pet-project упрощённой реализации **Git на Python**.  
Проект показывает базовые принципы работы системы контроля версий: инициализацию репозитория, добавление файлов в индекс, создание blob/tree/commit объектов и просмотр истории коммитов.  
Также проект демонстрирует применение **объектно-ориентированного программирования (OOP)** для моделирования внутренних сущностей Git.

## Features

- **Repository Initialization** — создание структуры репозитория и служебных файлов
- **Index Management** — добавление файлов в staging area
- **Git Objects** — работа с blob, tree и commit объектами
- **Hashing & Storage** — сохранение объектов по SHA-1 хэшу
- **Commit Creation** — создание коммитов на основе текущего состояния индекса
- **Commit History** — просмотр истории коммитов
- **CLI Commands** — поддержка команд через консольный интерфейс
- **OOP Design** — использование классов и абстракций для организации логики проекта

## Project Structure

- `pygit_commands.py` — реализация основных CLI-команд
- `objects.py` — модели Git-объектов (`Blob`, `Tree`, `Commit`)
- `index.py` — работа с индексом и построением tree-структуры
- `log.py` — вывод и обход истории коммитов
- `constants.py` — константы и базовые настройки проекта

## Tech Stack

- **Language:** Python
- **Paradigm:** Object-Oriented Programming (OOP)
- **Architecture:** modular CLI application
- **Concepts:** hashing, serialization, file system operations
- **Version Control Model:** simplified Git internals

## Project Goal

Цель проекта — лучше понять внутреннее устройство Git, попрактиковаться в Python, работе с файловой системой, хэшированием данных и объектно-ориентированным проектированием.
