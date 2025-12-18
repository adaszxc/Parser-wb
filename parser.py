# Извлекает данные из JSON и проверяет их корректность

from config import WB_PRICE_SELECT_MODE


# Извлекает id товаров из products (падает при отклонении)
def wb_parse_first_ids(products: list[dict], top_n: int) -> list[int]:
    if len(products) < top_n:
        raise RuntimeError(f"search: products меньше чем {top_n}: {len(products)}")

    ids: list[int] = []
    for i in range(top_n):
        item = products[i]
        nm_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(nm_id, int):
            raise RuntimeError(f"search: products[{i}].id не int: {nm_id!r}")
        ids.append(nm_id)

    return ids


# Извлекает имя и цены из JSON карточки (падает при отклонении)
def wb_parse_card_name_prices(cards_json: dict, nm_id: int) -> dict:
    data = cards_json.get("data")
    if isinstance(data, dict) and isinstance(data.get("products"), list):
        cards_products = data["products"]
    elif isinstance(cards_json.get("products"), list):
        cards_products = cards_json["products"]
    else:
        raise RuntimeError(
            f"cards: не найден products[] для id={nm_id}"
        )


    p_item = cards_products[0] if cards_products and isinstance(cards_products[0], dict) else None
    if not isinstance(p_item, dict):
        raise RuntimeError(f"cards: пустая карточка для id={nm_id}")

    name = p_item.get("name")
    if not isinstance(name, str):
        raise RuntimeError(f"cards: нет name для id={nm_id}")

    sizes = p_item.get("sizes")
    if not isinstance(sizes, list) or not sizes:
        raise RuntimeError(f"cards: нет sizes[] для id={nm_id}")

    basic_u: int | None = None
    wallet_u: int | None = None

    for s in sizes:
        if not isinstance(s, dict):
            continue
        price = s.get("price")
        if not isinstance(price, dict):
            continue

        b = price.get("basic")
        w = price.get("product")

        if isinstance(b, int):
            if WB_PRICE_SELECT_MODE == "min":
                basic_u = b if basic_u is None else min(basic_u, b)
            else:
                basic_u = b if basic_u is None else basic_u

        if isinstance(w, int):
            if WB_PRICE_SELECT_MODE == "min":
                wallet_u = w if wallet_u is None else min(wallet_u, w)
            else:
                wallet_u = w if wallet_u is None else wallet_u

    if basic_u is None or wallet_u is None:
        raise RuntimeError(f"cards: нет price.basic/product в sizes[] для id={nm_id}")

    return {
        "id": nm_id,
        "name": name,
        "basic": basic_u / 100,
        "wallet": wallet_u / 100,
    }
