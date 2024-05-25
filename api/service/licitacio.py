def SerializeLicitacio(charger):
    data = {
        "latitud": charger.latitud,
        "longitud": charger.longitud,
        "nom_organ": charger.promotorGestor,
        "tipus": "Servei",
        "procediment": "Obert",
        "fase_publicacio": "Formalització",
        "denominacio": "Servei de recàrrega de vehicles elèctrics",
        "lloc_execucio": charger.adreA,
        "nom_ambit": "PowerPathFinder",
        "pressupost": 3.69,
    }
    return data
