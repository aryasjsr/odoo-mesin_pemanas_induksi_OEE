# OEE Mesin Pemanas Induksi — Task Tracker

## Module 1: `mrp_shopfloor_custom` ✅
- [x] OWL Shop Floor (dark mode, tabs, cards, timers, operator clock-in/out)

## Module 2: `mrp_oee_custom` ✅
- [x] OEE computed fields + OWL dashboard

## Module 3: `mrp_quality_custom` ✅
- [x] Quality control points, checks, alerts, toast notifications

## Module 4: `mrp_oee_modbus` ✅
- [x] Scaffold: manifest, init files, security CSV
- [x] Model: `mrp.modbus.config` (14 fields + connection/polling methods)
- [x] Model: `mrp.modbus.register.map` (9 fields, 11 variable keys)
- [x] Model: extend `mrp.workcenter` with `modbus_config_id` + sync method
- [x] Service: [ModbusOEEClient](file:///d:/ARYA/SEMESTER%208/ENTERPRISE%20AUTOMATION/Odoo/addons/mrp_oee_modbus/services/modbus_client.py#20-249) (pymodbus read/write, connect/disconnect)
- [x] Wizard: `mrp.modbus.test.wizard` (test connection + read registers)
- [x] Views: config form/list, register map, workcenter button, menus
- [x] Data: default register map (Omron NB HMI), cron job

## Verification
- [x] `pip install pymodbus` in Docker
- [ ] Install module, create config, test connection
- [ ] Test with Modbus simulator
