class ChannelAdapterService:
    def normalize(self, payload: dict) -> dict:
        source = payload.get("source_channel", "api")
        photos = payload.get("photos", [])
        return {
            "source_channel": source,
            "photos": photos,
            "external_reference": payload.get("external_reference"),
        }
