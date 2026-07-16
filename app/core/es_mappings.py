LOGS_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "level": {"type": "keyword"},
            "message": {"type": "text"},
            "source_id": {"type": "keyword"},
            "project": {"type": "keyword"},
            "metadata": {"type": "object", "dynamic": True},
        }
    }
}
