/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class OeeDashboard extends Component {
    static template = "mrp_oee_custom.OeeDashboard";
    static props = { "*": true };

    setup() {
        this.state = useState({
            workcenters: [],
            loading: true,
            error: null,
            lastUpdate: null,
        });
        this._intervalId = null;

        onWillStart(async () => {
            await this.fetchData();
        });

        onMounted(() => {
            this._intervalId = setInterval(() => {
                this.fetchData();
            }, 5000);
        });

        onWillUnmount(() => {
            if (this._intervalId) {
                clearInterval(this._intervalId);
                this._intervalId = null;
            }
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
            const result = await this._rpc("/api/oee/dashboard_data", {});
            if (result.status === "ok") {
                this.state.workcenters = result.data;
                this.state.error = null;
            } else {
                this.state.error = result.message || "Unknown error";
            }
        } catch (err) {
            this.state.error = "Failed to fetch OEE data";
            console.error("OEE Dashboard fetch error:", err);
        }
        this.state.loading = false;
        this.state.lastUpdate = new Date().toLocaleTimeString();
    }

    getStatusColor(value) {
        if (value > 80) return "oee-good";
        if (value >= 60) return "oee-warning";
        return "oee-critical";
    }

    getCircleOffset(value) {
        const circumference = 339.292;
        const progress = Math.min(Math.max(value, 0), 100) / 100;
        return circumference - (progress * circumference);
    }

    getStateLabel(state) {
        return { stop: "Stopped", running: "Running", paused: "Paused" }[state] || "Unknown";
    }

    getStateClass(state) {
        return { stop: "state-stop", running: "state-running", paused: "state-paused" }[state] || "";
    }
}

registry.category("actions").add("oee_dashboard", OeeDashboard);
