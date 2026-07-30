#!/usr/bin/env python3
"""
Docs Search Prototype — Indexer

Читает все .xhtml / .html файлы из папки data/,
извлекает title, текст, метаданные и строит компактный JSON-индекс
для клиентского поиска (Fuse.js).

Использование:
    python indexer.py
    python indexer.py --data-dir ./data --output ./public/search-index.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Ошибка: установите зависимости: pip install -r requirements.txt")
    sys.exit(1)


def normalize_text(text: str) -> str:
    """Лёгкая нормализация текста."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(soup: BeautifulSoup, fallback: str) -> str:
    """Пытается достать заголовок из <title>, <h1> или первого заголовка."""
    # 1. <title>
    if soup.title and soup.title.string:
        t = normalize_text(soup.title.string)
        if t and t.lower() not in ("untitled", "confluence"):
            return t

    # 2. <h1>
    h1 = soup.find("h1")
    if h1:
        t = normalize_text(h1.get_text(" ", strip=True))
        if t:
            return t

    # 3. любой заголовок
    for tag in ("h2", "h3", "h4"):
        el = soup.find(tag)
        if el:
            t = normalize_text(el.get_text(" ", strip=True))
            if t:
                return t

    return fallback


def extract_text(soup: BeautifulSoup) -> str:
    """Извлекает основной текст, убирая скрипты, стили и навигацию."""
    # Удаляем ненужное
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()

    # Часто в Confluence XHTML много служебных div
    for el in soup.select("[class*='aui-'], [class*='confluence-'], .toc-macro, .navigation"):
        el.decompose()

    text = soup.get_text(" ", strip=True)
    return normalize_text(text)


def extract_headings(soup: BeautifulSoup) -> list[str]:
    """Собирает все заголовки h1–h4."""
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        t = normalize_text(tag.get_text(" ", strip=True))
        if t and len(t) > 1:
            headings.append(t)
    return headings[:20]  # ограничиваем


def process_file(path: Path) -> dict[str, Any] | None:
    """Обрабатывает один XHTML/HTML файл → документ для индекса."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] Не удалось прочитать {path.name}: {e}")
        return None

    # Парсим как XML (XHTML) или HTML
    soup = None
    try:
        # Предпочитаем XML-парсер для настоящего XHTML
        soup = BeautifulSoup(raw, "lxml-xml")
    except Exception:
        pass

    if soup is None or soup.find() is None:
        for parser in ("lxml", "html5lib", "html.parser"):
            try:
                soup = BeautifulSoup(raw, parser)
                if soup.find():
                    break
            except Exception:
                continue

    if soup is None or soup.find() is None:
        print(f"  [WARN] Не удалось распарсить {path.name}")
        return None

    file_id = path.stem  # имя файла без расширения (ID)
    title = extract_title(soup, fallback=file_id)
    body = extract_text(soup)
    headings = extract_headings(soup)

    # Короткий сниппет для отображения (первые ~300 символов)
    snippet = body[:300] + ("…" if len(body) > 300 else "")

    # Простые aliases / keywords из заголовка (для прототипа)
    aliases = []
    # Разбиваем camelCase / kebab и т.п. в заголовке
    words = re.findall(r"[A-Za-z0-9]+", title)
    aliases.extend(words)

    doc = {
        "id": file_id,
        "title": title,
        "aliases": list(dict.fromkeys(aliases)),  # unique, preserve order
        "headings": headings,
        "content": body[:8000],  # ограничиваем размер для клиентского индекса
        "snippet": snippet,
        "path": path.name,          # локальное имя файла
        "url": f"./data/{path.name}",  # ссылка, которую будет возвращать поиск
        "char_count": len(body),
        "word_count": len(body.split()),
    }
    return doc


def build_index(data_dir: Path) -> list[dict[str, Any]]:
    """Собирает индекс из всех .xhtml / .html файлов."""
    patterns = ("*.xhtml", "*.html", "*.htm")
    files: list[Path] = []
    for pat in patterns:
        files.extend(sorted(data_dir.glob(pat)))

    if not files:
        print(f"[ERROR] В папке {data_dir} не найдено ни одного .xhtml/.html файла")
        print("Положите ваши статьи в папку data/ и запустите скрипт снова.")
        sys.exit(1)

    print(f"Найдено файлов: {len(files)}")
    documents = []

    for i, path in enumerate(files, 1):
        print(f"  [{i}/{len(files)}] {path.name}")
        doc = process_file(path)
        if doc:
            documents.append(doc)

    print(f"\nУспешно проиндексировано: {len(documents)} документов")
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Docs Search Prototype Indexer")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Папка с XHTML/HTML статьями (по умолчанию: ./data)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("public/search-index.json"),
        help="Куда сохранить JSON-индекс (по умолчанию: ./public/search-index.json)",
    )
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    output: Path = args.output

    if not data_dir.is_dir():
        print(f"[ERROR] Папка {data_dir} не существует.")
        print("Создайте её и положите туда .xhtml файлы:")
        print(f"  mkdir -p {data_dir}")
        sys.exit(1)

    documents = build_index(data_dir)

    # Финальный объект индекса
    index = {
        "version": 1,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "document_count": len(documents),
        "documents": documents,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    # Копируем исходные файлы в public/data/, чтобы ссылки в UI работали
    public_data = output.parent / "data"
    public_data.mkdir(parents=True, exist_ok=True)
    import shutil
    copied = 0
    for src in data_dir.glob("*"):
        if src.suffix.lower() in {".xhtml", ".html", ".htm"}:
            dst = public_data / src.name
            shutil.copy2(src, dst)
            copied += 1
    print(f"Скопировано файлов статей в {public_data}: {copied}")

    size_kb = output.stat().st_size / 1024
    print(f"\nИндекс сохранён: {output} ({size_kb:.1f} KB)")
    print("Готово. Запустите сервер из папки public/ и откройте http://localhost:8000")


if __name__ == "__main__":
    main()
