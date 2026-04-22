# Energidata
This repo is for implementing various energi data related APIs
Install via:
    pip install git+https://github.com/petermads123/energidata.git@main
or in dependecies in pyproject.toml:
    "energidata @ git+https://github.com/petermads123/energidata.git@main"

## Energidataservice
Energinets energidataservice for danish energy system data.
### Ready to use
- Day ahead prices (energidata.energidataservice.get_dayahead_prices)
- Imbalance prices (energidata.energidataservice.get_imbalance_prices)
### Planned / under development
- mFFR and aFFR prices and activation volumes
- DSO tariffs (energidata.energidataservice.get_dso_tariffs)

## Eloverblik
Energinets datahub eloverblik for meter related data.
Note that these APIs require access tokens.
### Ready to use
None
### Planned / under development
- Meter data (energidata.eloverblik.get_meter_data)

## ENTSO-e
ENTSO-Es transparency platform API service, for european-wide prices and energy system data.
### Ready to use
None
### Planned / under development
- Day ahead prices (energidata.entsoe.get_dayahead_prices)
- Imbalance prices (energidata.entsoe.get_imbalance_prices)
