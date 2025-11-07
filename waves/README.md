# Waves Configuration

This directory contains module installation order files ("waves"). Each wave file lists modules that should be installed together in a specific order.

## Wave Files

- **00_base.txt**: Core Odoo modules
- **10_web_ux.txt**: Web interface and UX enhancements
- **20_sales_inventory.txt**: Sales and inventory management
- **25_localization.txt**: Localization and accounting base
- **30_accounting.txt**: Advanced accounting features
- **40_hr_project.txt**: HR and project management
- **50_ipai_custom.txt**: Custom IPAI modules
- **90_optional.txt**: Optional modules

## Usage

Waves are processed in numerical order by the `install_waves.sh` script:

```bash
bash scripts/install_waves.sh odoo18
```

Or from inside the Odoo container:

```bash
docker compose -f docker/docker-compose.odoo18.yml exec odoo bash -c "bash /mnt/scripts/install_waves.sh odoo18"
```

## Format

Each wave file should contain one module name per line:

```
module_name_1
module_name_2
module_name_3
```

Empty lines and lines starting with `#` are ignored.

## Notes

- Modules are installed with `--stop-after-init` flag
- Each wave completes before the next one starts
- Failed installations will halt the process
- Some modules may not be available if OCA repositories haven't been cloned
