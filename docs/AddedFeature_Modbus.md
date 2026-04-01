## ADDED FEATURE MODBUS
Your task is to build a custom Odoo addon module named `mrp_oee_modbus` that adds
a fully configurable Modbus TCP/IP interface for reading real-time machine data
(used to compute OEE) and writing OEE results back to an Omron NB HMI via
Modbus TCP/IP protocol.

The system architecture is:
  [Induction Heating Machine] → Modbus TCP/IP → [Odoo MRP OEE Module]
                                                        ↓
                                               [Writes OEE to HMI via Modbus TCP/IP]
  [Omron NB HMI] ← Modbus TCP/IP ← [mrp_oee_modbus Odoo Service]

---

## MODULE STRUCTURE TO CREATE

Create a full Odoo addon at path: `addons/mrp_oee_modbus/`

Required file structure:
```
mrp_oee_modbus/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── modbus_config.py        # Modbus connection config model
│   ├── modbus_register_map.py  # Register address mapping model
│   └── mrp_workcenter.py       # Extend workcenter with Modbus config
├── services/
│   ├── __init__.py
│   └── modbus_client.py        # pymodbus TCP client service
├── wizards/
│   ├── __init__.py
│   └── modbus_test_wizard.py   # Connection test wizard
├── views/
│   ├── modbus_config_views.xml
│   ├── modbus_register_map_views.xml
│   └── menus.xml
├── security/
│   └── ir.model.access.csv
└── data/
    └── default_register_map.xml
```

---

## DETAILED REQUIREMENTS

### 1. MODEL: `modbus_config.py` — `mrp.modbus.config`

Create an Odoo model with the following fields:

| Field Name          | Type        | Description                                      | Default     |
|---------------------|-------------|--------------------------------------------------|-------------|
| name                | Char        | Config profile name (e.g., "Mesin Induksi #1")   | Required    |
| host                | Char        | IP address of Modbus TCP server (PLC/HMI)        | "192.168.1.1"|
| port                | Integer     | Modbus TCP port                                  | 502         |
| slave_id            | Integer     | Modbus Unit ID / Slave ID                        | 1           |
| timeout             | Float       | Connection timeout in seconds                    | 3.0         |
| retries             | Integer     | Number of retries on failure                     | 3           |
| reconnect_delay     | Float       | Delay in seconds before reconnect                | 0.1         |
| polling_interval    | Integer     | Data polling interval in seconds                 | 5           |
| is_active           | Boolean     | Enable/disable this config                       | True        |
| connection_status   | Selection   | ['connected', 'disconnected', 'error']           | 'disconnected'|
| last_connected      | Datetime    | Timestamp of last successful connection          |             |
| workcenter_id       | Many2one    | Link to `mrp.workcenter`                         |             |
| register_map_ids    | One2many    | Link to register map lines                       |             |
| notes               | Text        | Optional notes / description                     |             |

Add methods:
- `action_test_connection(self)` → Try to connect using pymodbus, update `connection_status` and `last_connected`, return notification wizard.
- `action_start_polling(self)` → Trigger background polling (use `ir.cron` or `threading`).
- `action_stop_polling(self)` → Stop the polling.
- `_get_client(self)` → Return configured `ModbusTcpClient` instance using self fields.

---

### 2. MODEL: `modbus_register_map.py` — `mrp.modbus.register.map`

This model maps logical OEE variables to actual Modbus register addresses.

| Field Name          | Type        | Description                                               |
|---------------------|-------------|-----------------------------------------------------------|
| config_id           | Many2one    | Parent Modbus config                                      |
| name                | Char        | Variable name (e.g., "Run Time", "OEE Value")             |
| variable_key        | Selection   | Predefined key from list below                            |
| register_type       | Selection   | ['holding', 'input', 'coil', 'discrete']                  |
| register_address    | Integer     | Modbus register address (0-based)                         |
| data_type           | Selection   | ['uint16', 'int16', 'float32', 'bool']                    |
| scale_factor        | Float       | Multiply raw value by this factor (e.g., 0.01 for %)      |
| direction           | Selection   | ['read', 'write', 'read_write']                           |
| description         | Text        | Human-readable description                                |

`variable_key` selection must include at minimum:
- `planned_time`        → Total planned production time (minutes)
- `run_time`            → Actual machine run time (minutes)
- `downtime`            → Machine downtime (minutes)
- `produced_qty`        → Actual quantity produced
- `ideal_qty`           → Ideal/target quantity
- `defect_qty`          → Rejected/defective quantity
- `machine_status`      → Machine ON/OFF status (coil/bool)
- `oee_availability`    → OEE Availability % (write to HMI)
- `oee_performance`     → OEE Performance % (write to HMI)
- `oee_quality`         → OEE Quality % (write to HMI)
- `oee_overall`         → OEE Overall % (write to HMI)

---

### 3. SERVICE: `modbus_client.py`

Create a service class `ModbusOEEClient` with:

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

class ModbusOEEClient:
    def __init__(self, config_record):
        # Initialize from mrp.modbus.config record

    def connect(self) -> bool:
        # Connect using ModbusTcpClient(host, port=port, timeout=timeout, retries=retries)
        # Return True if successful

    def disconnect(self):
        # Close client connection

    def read_register(self, register_address, register_type, data_type, scale_factor) -> float | bool:
        # Read a single register based on type: holding/input/coil/discrete
        # Apply scale_factor to numeric values
        # Handle ModbusException gracefully, log error and return None

    def write_register(self, register_address, value, data_type, scale_factor):
        # Write OEE results back to HMI
        # For float32: write two consecutive holding registers (high word, low word)
        # For uint16/int16: write single holding register
        # Apply inverse scale_factor before writing

    def read_all_oee_inputs(self, register_map_records) -> dict:
        # Iterate register_map_records where direction in ('read', 'read_write')
        # Return dict: {variable_key: value}

    def write_all_oee_outputs(self, register_map_records, oee_results: dict):
        # Iterate register_map_records where direction in ('write', 'read_write')
        # Write each OEE result to corresponding register
```

Requirements for the service:
- Use `pymodbus >= 3.5.0` synchronous client `ModbusTcpClient`
- Default port: **502** for Modbus TCP [per pymodbus standard]
- Default slave_id: **1**
- Must handle exception response with `rr.isError()` check
- Add Python `logging` for all operations
- Add connection retry logic with configurable `retries` and `reconnect_delay`

---

### 4. EXTEND: `mrp.workcenter` (in `mrp_workcenter.py`)

Add field to native `mrp.workcenter`:
```python
modbus_config_id = fields.Many2one('mrp.modbus.config', string='Modbus Configuration')
```

Add method:
```python
def action_sync_oee_from_modbus(self):
    # 1. Get modbus_config_id
    # 2. Instantiate ModbusOEEClient
    # 3. Connect
    # 4. Read all input registers → get dict of variable values
    # 5. Compute OEE:
    #    availability = run_time / planned_time
    #    performance  = produced_qty / ideal_qty
    #    quality      = (produced_qty - defect_qty) / produced_qty
    #    oee_overall  = availability * performance * quality * 100
    # 6. Write OEE results back to HMI output registers
    # 7. Update/create mrp.workcenter.productivity records in Odoo
    # 8. Disconnect
    # 9. Return action notification
```

---

### 5. WIZARD: `modbus_test_wizard.py`

Create wizard model `mrp.modbus.test.wizard` with:
- `config_id` (Many2one)
- `test_result` (Text, readonly)
- `connection_ok` (Boolean, readonly)

Action `action_run_test`:
1. Instantiate `ModbusOEEClient`
2. Attempt connect
3. Try reading each active register in the register map
4. Display results in `test_result` field
5. Show green/red status based on `connection_ok`

---

### 6. VIEWS (`modbus_config_views.xml`)

Create:
1. **Form View** for `mrp.modbus.config`:
   - Group: Connection Settings (host, port, slave_id, timeout, retries, reconnect_delay, polling_interval)
   - Group: Status (connection_status, last_connected, is_active)
   - Notebook tab: "Register Map" → inline editable One2many list
   - Button bar: "Test Connection", "Start Polling", "Stop Polling"
   - Status bar widget for `connection_status`

2. **List View** for `mrp.modbus.config`

3. **Form View** for `mrp.modbus.register.map` (standalone)

4. Add button "Sync OEE from Modbus" in `mrp.workcenter` form view

---

### 7. SCHEDULED ACTION (ir.cron via data XML)

Create an `ir.cron` record that:
- Calls `mrp.modbus.config` → method `_cron_poll_all_active_configs()`
- Runs every **polling_interval** seconds (use 5 seconds as default minimum)
- Is active only when at least one config has `is_active = True`

`_cron_poll_all_active_configs` must:
1. Search all `mrp.modbus.config` where `is_active = True`
2. For each config, call `action_sync_oee_from_modbus` on linked workcenter
3. Log results to `ir.logging` or `mail.message` on the config record

---

### 8. `__manifest__.py` requirements

```python
{
    'name': 'MRP OEE Modbus Integration',
    'version': '1.0.0',
    'category': 'Manufacturing',
    'depends': ['mrp', 'mrp_workcenter'],
    'external_dependencies': {'python': ['pymodbus']},
    'data': [
        'security/ir.model.access.csv',
        'data/default_register_map.xml',
        'views/modbus_config_views.xml',
        'views/modbus_register_map_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
}
```

---

### 9. DEFAULT DATA (`default_register_map.xml`)

Create a default register map template for Omron NB HMI (typical Modbus TCP register layout):

| variable_key       | register_address | register_type | data_type | scale_factor | direction   |
|--------------------|-----------------|---------------|-----------|--------------|-------------|
| planned_time       | 0               | holding       | uint16    | 1.0          | read        |
| run_time           | 1               | holding       | uint16    | 1.0          | read        |
| downtime           | 2               | holding       | uint16    | 1.0          | read        |
| produced_qty       | 3               | holding       | uint16    | 1.0          | read        |
| ideal_qty          | 4               | holding       | uint16    | 1.0          | read        |
| defect_qty         | 5               | holding       | uint16    | 1.0          | read        |
| machine_status     | 0               | coil          | bool      | 1.0          | read        |
| oee_availability   | 10              | holding       | uint16    | 0.01         | write       |
| oee_performance    | 11              | holding       | uint16    | 0.01         | write       |
| oee_quality        | 12              | holding       | uint16    | 0.01         | write       |
| oee_overall        | 13              | holding       | uint16    | 0.01         | write       |

(Note: scale_factor 0.01 means Odoo writes integer 8550 → HMI interprets as 85.50%)

---

## CODING CONSTRAINTS & BEST PRACTICES

1. Use Odoo ORM properly — no raw SQL unless justified.
2. All pymodbus calls must be wrapped in `try/except ModbusException`.
3. Use `_logger = logging.getLogger(__name__)` in every Python file.
4. Connection must be closed in `finally` block to prevent socket leaks.
5. OEE formula:
   - Availability  = run_time / planned_time
   - Performance   = produced_qty / ideal_qty
   - Quality       = (produced_qty − defect_qty) / produced_qty
   - OEE Overall   = Availability × Performance × Quality × 100 (%)
6. Division by zero must be handled explicitly (return 0.0).
7. Register addresses are 0-based (pymodbus standard).
8. For Omron NB HMI compatibility, use `FramerType.SOCKET` (default for TCP).
9. All config fields must have proper `_sql_constraints` for uniqueness where needed.
10. The module must work with Odoo 16 or 17 Community Edition.

---

## DELIVERABLE

Produce complete, runnable Python and XML code for all files listed in the
module structure above. Each file must be complete — no placeholder comments
like "# TODO: implement this". Include all imports, class definitions,
method bodies, and XML records.
```