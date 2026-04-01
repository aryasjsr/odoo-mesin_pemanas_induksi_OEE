/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class QualityDashboard extends Component {
    static template = "mrp_quality_custom.QualityDashboard";
    static props = { "*": true };

    setup() {
        this.action = useService("action");

        this.state = useState({
            pendingCount: 0,
            alertCount: 0,
            recentChecks: [],
            loading: true,
            error: null,
            lastUpdate: null,
        });

        this._intervalId = null;

        onWillStart(async () => {
            await this.fetchData();
        });

        onMounted(() => {
            this._intervalId = setInterval(() => this.fetchData(), 5000);
        });

        onWillUnmount(() => {
            if (this._intervalId) clearInterval(this._intervalId);
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

    async fetchData() {
        try {
            const result = await this._rpc("/api/quality/dashboard_data", {});
            if (result.status === "ok") {
                this.state.pendingCount = result.pending_count;
                this.state.alertCount = result.alert_count;
                this.state.recentChecks = result.recent_checks;
                this.state.error = null;
            }
        } catch (err) {
            this.state.error = "Failed to load quality data";
        }
        this.state.loading = false;
        this.state.lastUpdate = new Date().toLocaleTimeString();
    }

    openChecks() {
        this.action.doAction("mrp_quality_custom.action_quality_check");
    }

    openAlerts() {
        this.action.doAction("mrp_quality_custom.action_quality_alert");
    }

    getStateClass(state) {
        return { todo: "qd-state-todo", pass: "qd-state-pass", fail: "qd-state-fail" }[state] || "";
    }

    getStateLabel(state) {
        return { todo: "Pending", pass: "Pass", fail: "Fail" }[state] || state;
    }
}

registry.category("actions").add("quality_dashboard", QualityDashboard);
