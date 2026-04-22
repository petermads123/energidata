# Energidata
This repo is for implementing various energi data related APIs
Install via:
    pip install git+https://github.com/petermads123/energidata.git@main
or in dependecies in pyproject.toml:
    "energidata @ git+https://github.com/petermads123/energidata.git@main"
    

## Energidataservice
Energinets energidataservice for energy system level data.
### Ready to use
- Day ahead prices (energidata.get_dayahead_prices)
- Imbalance prices (energidata.get_imbalance_prices)
### Planned / under development
- mFFR and aFFR prices and activation volumes
- DSO tariffs (energidata.get_dso_tariffs)

## Eloverblik
Energinets datahub eloverblik for meter related data.
Note that these APIs require access tokens.
### Ready to use
None
### Planned / under development
- Meter data (energidata.get_meter_data)
