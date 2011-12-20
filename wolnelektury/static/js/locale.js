var LOCALE_TEXTS = {
    "pl": {
        "Loading": "Ładowanie"
    },
    "de": {
        "Loading": "Herunterladen"
    },
    "fr": {
        "Loading": "Chargement"
    },
    "en": {
        "Loading": "Loading"
    },
    "ru": {
        "Loading": "Загрузка"
    },
    "es": {
        "Loading": "Cargando"
    },
    "lt":{
        "Loading": "Krovimas"
    },
    "uk":{
        "Loading": "Завантажується"
    }
}
function gettext(text) {
    return LOCALE_TEXTS[LANGUAGE_CODE][text];
}