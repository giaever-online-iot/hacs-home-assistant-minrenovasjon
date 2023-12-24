"""Constants for the MinRenovasjon integration."""

DOMAIN = "minrenovasjon"

KOMMUNE_NUMMER = "Kommunenr"

APP_KEY = "RenovasjonAppKey"
APP_KEY_VALUE = "AE13DEEC-804F-4615-A74E-B4FAC11F0A30"

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

URL_PROXY = 'https://norkartrenovasjon.azurewebsites.net/proxyserver.ashx'
URL_FRACTIONS = "https://komteksky.norkart.no/MinRenovasjon.Api/api/fraksjoner"
URL_CALENDAR = "https://komteksky.norkart.no/MinRenovasjon.Api/api/tommekalender/"
URL_CALENDAR_STREET_NAME = {"gatenavn": "{}"}
URL_CALENDAR_STREET_CODE = {"gatekode": "{}"}
URL_CALENDAR_HOUSE_NUMBER = {"husnr": "{}"}
URL_SEARCH_HOUSEHOLD = "https://ws.geonorge.no/adresser/v1/sok?sok={street_address}"
