def get_total_pages(count_products, max_quantity):
    pages = count_products // max_quantity
    if count_products % max_quantity != 0:
        pages += 1
    return pages
