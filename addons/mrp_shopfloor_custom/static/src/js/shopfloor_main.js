/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ShopFloor extends Component {
    static template = "mrp_shopfloor_custom.ShopFloor";
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");

        this.state = useState({
            workcenters: [],
            selectedWcId: null,
            workOrders: [],
            operators: [],
            loading: true,
            error: null,
            // Operator filter
            selectedOperatorId: null,
            // Instructions dialog
            showInstructions: false,
            instructionsText: "",
            // Production dialog
            showProductionDialog: false,
            productionWoId: null,
            productionQty: 0,
            // Scrap dialog
            showScrapDialog: false,
            scrapWoId: null,
            scrapQty: 0,
            // Block dialog
            showBlockDialog: false,
            blockWoId: null,
            blockLossId: null,
            lossReasons: [],
        });

        this._intervalId = null;
        this._timerIntervalId = null;

        onWillStart(async () => {
            await this.fetchData();
            await this.fetchLossReasons();
        });

        onMounted(() => {
            this._intervalId = setInterval(() => this.fetchData(), 5000);
            this._timerIntervalId = setInterval(() => this._tickTimers(), 1000);
        });

        onWillUnmount(() => {
            if (this._intervalId) clearInterval(this._intervalId);
            if (this._timerIntervalId) clearInterval(this._timerIntervalId);
        });
    }

    async _rpc(route, params = {}) {
        const response = await fetch(route, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params }),
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error.message || "RPC Error");
        return data.result;
    }

    // ---- Data fetching ----

    async fetchData() {
        try {
            const result = await this._rpc("/api/shopfloor/data", {
                workcenter_id: this.state.selectedWcId || false,
            });
            if (result.status === "ok") {
                this.state.workcenters = result.workcenters;
                if (!this.state.selectedWcId && result.workcenters.length > 0) {
                    this.state.selectedWcId = result.workcenters[0].id;
                }
                this.state.workOrders = result.work_orders;
                this.state.operators = result.operators;
                this.state.error = null;
            } else {
                this.state.error = result.message;
            }
        } catch (err) {
            this.state.error = "Connection error";
        }
        this.state.loading = false;
    }

    async fetchLossReasons() {
        try {
            const result = await this._rpc("/api/shopfloor/loss_reasons");
            if (result.status === "ok") {
                this.state.lossReasons = result.loss_reasons;
            }
        } catch (err) {
            console.error("Failed to fetch loss reasons:", err);
        }
    }

    // ---- Timer ----

    _tickTimers() {
        for (const wo of this.state.workOrders) {
            if (wo.machine_state === "running") {
                wo.running_seconds = (wo.running_seconds || 0) + 1;
            } else if (wo.machine_state === "paused") {
                wo.current_blocked_seconds = (wo.current_blocked_seconds || 0) + 1;
            }
        }
    }

    formatTimer(seconds) {
        const s = seconds || 0;
        const h = Math.floor(s / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
    }

    // ---- Workcenter tabs ----

    selectWorkcenter(wcId) {
        this.state.selectedWcId = wcId;
        this.state.loading = true;
        this.fetchData();
    }

    isSelectedWc(wcId) {
        return this.state.selectedWcId === wcId;
    }

    // ---- Operator sidebar ----

    selectOperator(userId) {
        if (this.state.selectedOperatorId === userId) {
            // Deselect: show all WOs again
            this.state.selectedOperatorId = null;
        } else {
            this.state.selectedOperatorId = userId;
        }
    }

    isSelectedOperator(userId) {
        return this.state.selectedOperatorId === userId;
    }

    get filteredWorkOrders() {
        if (!this.state.selectedOperatorId) {
            return this.state.workOrders;
        }
        return this.state.workOrders.filter(
            (wo) => wo.responsible_user_id === this.state.selectedOperatorId
        );
    }

    // ---- Machine actions ----

    async onStart(woId) {
        try {
            await this._rpc("/api/machine/start", { wo_id: woId });
            this.notification.add("Machine started — auto clock-in ✅", { type: "success" });
            await this.fetchData();
        } catch (err) {
            this.notification.add("Start failed: " + err.message, { type: "danger" });
        }
    }

    async onResume(woId) {
        try {
            await this._rpc("/api/machine/resume", { wo_id: woId });
            this.notification.add("Machine resumed ✅", { type: "success" });
            await this.fetchData();
        } catch (err) {
            this.notification.add("Resume failed: " + err.message, { type: "danger" });
        }
    }

    // ---- Block (pause with loss reason) ----

    openBlockDialog(woId) {
        this.state.blockWoId = woId;
        this.state.blockLossId = this.state.lossReasons.length > 0 ? this.state.lossReasons[0].id : null;
        this.state.showBlockDialog = true;
    }

    async submitBlock() {
        if (!this.state.blockLossId) {
            this.notification.add("Please select a loss reason", { type: "warning" });
            return;
        }
        try {
            await this._rpc("/api/machine/block", {
                wo_id: this.state.blockWoId,
                loss_id: this.state.blockLossId,
            });
            const reason = this.state.lossReasons.find((r) => r.id === this.state.blockLossId);
            this.notification.add(`Machine blocked: ${reason ? reason.name : "Unknown"} ⚠️`, { type: "warning" });
            this.state.showBlockDialog = false;
            await this.fetchData();
        } catch (err) {
            this.notification.add("Block failed: " + err.message, { type: "danger" });
        }
    }

    // ---- Production dialog ----

    openProductionDialog(woId) {
        const wo = this.state.workOrders.find((w) => w.id === woId);
        this.state.productionWoId = woId;
        this.state.productionQty = wo ? wo.good_count : 0;
        this.state.showProductionDialog = true;
    }

    onProductionQtyInput(ev) {
        this.state.productionQty = parseInt(ev.target.value) || 0;
    }

    async submitProduction() {
        const qty = parseInt(this.state.productionQty) || 0;
        if (qty >= 0) {
            try {
                const wo = this.state.workOrders.find((w) => w.id === this.state.productionWoId);
                await this._rpc("/api/machine/update_count", {
                    wo_id: this.state.productionWoId,
                    good_count: qty,
                    reject_count: wo ? wo.reject_count : 0,
                });
                this.notification.add(`Production updated: ${qty} units ✅`, { type: "success" });
            } catch (err) {
                this.notification.add("Update failed: " + err.message, { type: "danger" });
            }
        }
        this.state.showProductionDialog = false;
        await this.fetchData();
    }

    // ---- Scrap dialog ----

    openScrapDialog(woId) {
        this.state.scrapWoId = woId;
        this.state.scrapQty = 1;
        this.state.showScrapDialog = true;
    }

    onScrapQtyInput(ev) {
        this.state.scrapQty = parseInt(ev.target.value) || 0;
    }

    async submitScrap() {
        const qty = parseInt(this.state.scrapQty) || 0;
        if (qty > 0) {
            try {
                await this._rpc("/api/machine/scrap", {
                    wo_id: this.state.scrapWoId,
                    reject_qty: qty,
                });
                this.notification.add(`Scrapped ${qty} units 🗑️`, { type: "danger" });
            } catch (err) {
                this.notification.add("Scrap failed: " + err.message, { type: "danger" });
            }
        }
        this.state.showScrapDialog = false;
        await this.fetchData();
    }

    // ---- Close production ----

    async onCloseProduction(woId) {
        try {
            await this._rpc("/api/shopfloor/close_production", { wo_id: woId });
            this.notification.add("Production closed ✅ Work Order done!", { type: "success" });
            await this.fetchData();
        } catch (err) {
            this.notification.add("Close failed: " + err.message, { type: "danger" });
        }
    }

    // ---- Dialogs ----

    closeDialog() {
        this.state.showProductionDialog = false;
        this.state.showScrapDialog = false;
        this.state.showInstructions = false;
        this.state.showBlockDialog = false;
    }

    openInstructions(notes) {
        this.state.instructionsText = notes || "No work instructions available for this operation.";
        this.state.showInstructions = true;
    }

    // ---- Helpers ----

    getStateLabel(s) {
        return { stop: "Stopped", running: "Running", paused: "Blocked" }[s] || "Unknown";
    }

    getStateBadgeClass(s) {
        return { stop: "sf-badge-stop", running: "sf-badge-running", paused: "sf-badge-paused" }[s] || "";
    }
}

registry.category("actions").add("shopfloor_main", ShopFloor);
