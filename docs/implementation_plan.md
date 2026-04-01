# Module 4: `mrp_oee_modbus` — Implementation Plan

Implements [AddedFeature_Modbus.md](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/docs/AddedFeature_Modbus.md): Modbus TCP config module for reading machine data and writing OEE results to Omron NB HMI.

## User Review Required

> [!IMPORTANT]
> **Dependency**: Spec says `depends: ['mrp', 'mrp_workcenter']` but `mrp_workcenter` is not a separate module. Will use `depends: ['mrp', 'mrp_oee_custom']` since we need the OEE computed fields.

> [!IMPORTANT]
> **pymodbus in Docker**: The Odoo Docker container needs `pymodbus >= 3.5.0`. Will add `external_dependencies: {'python': ['pymodbus']}` to manifest. You'll need to `docker compose exec web pip install pymodbus` before installing the module.

> [!WARNING]
> **Threading/Cron**: The spec mentions `ir.cron` for polling, but Odoo cron has a minimum 1-minute interval. For 5-second polling, will use `ir.cron` as the "start" mechanism that spawns a background thread. Thread stops on `action_stop_polling()`.

---

## Proposed Changes

### Module 4: `mrp_oee_modbus` (NEW)

#### [NEW] [\_\_manifest\_\_.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/__manifest__.py)
- Depends: `['mrp', 'mrp_oee_custom']`
- External: `{'python': ['pymodbus']}`
- Data: security, default register map, views, menus, cron

#### [NEW] [models/modbus\_config.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/models/modbus_config.py)
Model `mrp.modbus.config` — 14 fields per spec + methods:
- `action_test_connection()` → connect, report, return wizard
- `action_start_polling()` → start background thread
- `action_stop_polling()` → signal thread to stop
- `_get_client()` → return configured `ModbusOEEClient`
- `_cron_poll_all_active_configs()` → cron entry point

#### [NEW] [models/modbus\_register\_map.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/models/modbus_register_map.py)
Model `mrp.modbus.register.map` — 9 fields, 11 variable_key selections, SQL constraint on unique (config_id, variable_key)

#### [NEW] [models/mrp\_workcenter.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/models/mrp_workcenter.py)
Extends `mrp.workcenter` with:
- `modbus_config_id` Many2one field
- `action_sync_oee_from_modbus()` — read registers, compute OEE, write back, update productivity

#### [NEW] [services/modbus\_client.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/services/modbus_client.py)
Class `ModbusOEEClient`:
- `connect()`, `disconnect()`, `read_register()`, `write_register()`
- `read_all_oee_inputs()`, `write_all_oee_outputs()`
- Uses `pymodbus.client.ModbusTcpClient`, error handling with `isError()`

#### [NEW] [wizards/modbus\_test\_wizard.py](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/wizards/modbus_test_wizard.py)
Wizard `mrp.modbus.test.wizard` — test connection + read all registers, display results

#### [NEW] [views/modbus\_config\_views.xml](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/views/modbus_config_views.xml)
Form view (connection settings, status, register map notebook tab, buttons) + list view

#### [NEW] [views/modbus\_register\_map\_views.xml](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/views/modbus_register_map_views.xml)
Standalone form + inline list for register map entries

#### [NEW] [views/menus.xml](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/views/menus.xml)
Menu: Manufacturing → Modbus Configuration + Register Map

#### [NEW] [data/default\_register\_map.xml](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/data/default_register_map.xml)
Default Omron NB HMI register layout (11 registers per spec table §9)

#### [NEW] [data/modbus\_cron.xml](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/data/modbus_cron.xml)
`ir.cron` calling `_cron_poll_all_active_configs()` every 1 minute (thread does 5s polling inside)

---

## Verification Plan

### Install
```bash
docker compose exec web pip install pymodbus
docker compose restart web
# Install mrp_oee_modbus from Apps
```

### Configuration
1. Create Modbus Config → fill IP/port for HMI simulator
2. Register map auto-loaded from defaults
3. Test Connection button → wizard shows success/fail + register readings

### Polling
1. Link config to a Work Center
2. "Start Polling" → thread starts, reads registers every 5s
3. OEE values update on OEE Dashboard
4. HMI output registers get written with OEE results
5. "Stop Polling" → thread stops gracefully

### User Manual Test
- User can test with **Modbus Poll** (Windows) or **ModRSsim2** as a simulator
