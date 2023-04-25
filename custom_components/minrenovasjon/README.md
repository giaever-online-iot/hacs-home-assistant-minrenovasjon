# MinRenovasjon
MinRenovasjon offers calendar and binary sensors for a given address in Home Assistant.

## Installation

### Using HACS

Copy the repository URL (`git@github.com:giaever-online-iot/hacs-home-assistant-minrenovasjon.git`) and add it as a custom repository in HACS.
1. Go into HACS
2. Click the three dots in the upper right corner
2.1 Select «Custom repositories» and paste the URL into the repository-field.
2.2 Select «Integration» as the category
2.3 Press «Add»
3. It should now show up under integration tab, flagged as a «New repository».
3.1 Click this badge and select «Download»

If the badge didn't show up or you accidentally dismissed it, you should find it by pressing the «+ Explore and download» button in the lower right corner. Search for «MinRenovasjon».

## Manual installation
Download the zipped version (`https://github.com/giaever-online-iot/hacs-home-assistant-minrenovasjon/archive/refs/heads/main.zip`) of the repository and copy the folder «custom_componets» into the root of your Home Assistant config folder.

## Configuration

Note! This integration do not support YAML-configuration.

1. Go into settings on your Home Assistant instance.
2. Select «Devices & Services» and click the «+ Add integration» button in the lower right corner.
3. Search for «MinRenovasjon» and follow the on-screen steps.