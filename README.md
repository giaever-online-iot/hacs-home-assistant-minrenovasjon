# MinRenovasjon
MinRenovasjon offer a calendar and binary sensors (for each fraction) for a given address in Home Assistant. It supperts multiple setups, for multiple addresses.

[Kooha-2023-04-25-18-45-44](https://user-images.githubusercontent.com/7188121/234346833-ac5c5d48-a36d-4097-bfd0-d83358ee1ef7.gif)

## Installation

### Using HACS

Copy the repository URL (`git@github.com:giaever-online-iot/hacs-home-assistant-minrenovasjon.git`) and add it as a custom repository in HACS.
1. Go into HACS
2. Click the three dots in the upper right corner
  - Select «Custom repositories» and paste the URL into the repository-field.
  - Select «Integration» as the category
  - Press «Add»

3. It should now show up under integration tab, flagged as a «New repository».
4. Click this badge and select «Download»

If the badge didn't show up or you accidentally dismissed it, you should find it by pressing the «+ Explore and download» button in the lower right corner. Search for «MinRenovasjon».

## Manual installation
Download the zipped version (`https://github.com/giaever-online-iot/hacs-home-assistant-minrenovasjon/archive/refs/heads/main.zip`) of the repository and copy the folder «custom_componets» into the root of your Home Assistant config folder.

## Configuration

Note! This integration do not support YAML-configuration.

1. Go into settings on your Home Assistant instance.
2. Select «Devices & Services» and click the «+ Add integration» button in the lower right corner.
3. Search for «MinRenovasjon» and follow the on-screen steps.!
