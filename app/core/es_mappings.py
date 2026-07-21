LOGS_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "level": {"type": "keyword"},
            "message": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 512}},
            },
            "source_id": {"type": "keyword"},
            "project": {"type": "keyword"},
            "metadata": {"type": "object", "dynamic": True},
        }
    }
}
