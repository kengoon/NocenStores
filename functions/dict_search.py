def search_engine(search_term, data_key, data):
    a = filter(lambda search_found: search_term in search_found[data_key], data)
    return list(a)
