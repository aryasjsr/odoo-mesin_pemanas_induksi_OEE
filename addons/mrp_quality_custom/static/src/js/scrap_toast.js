/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * ScrapToast — Global systray component that polls for reject count changes
 * and shows a slide-in toast notification at the top-right corner.
 */
class ScrapToast extends Component {
    static template = "mrp_quality_custom.ScrapToast";
    static props = {};

    setup() {
        this.state = useState({
            toasts: [],
        });
        this._lastRejectCounts = {};
        this._intervalId = null;
        this._toastIdCounter = 0;

        onMounted(() => {
            this._intervalId = setInterval(() => this.pollRejects(), 5000);
        });

        onWillUnmount(() => {
            if (this._intervalId) clearInterval(this._intervalId);
        });
    }

    async _rpc(route, params = {}) {
        try {
            const response = await fetch(route, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ jsonrpc: "2.0", method: "call", params }),
            });
            const data = await response.json();
            if (data.error) return null;
            return data.result;
        } catch {
            return null;
        }
    }

    async pollRejects() {
        const result = await this._rpc("/api/shopfloor/data", {});
        if (result && result.status === "ok" && result.work_orders) {
            for (const wo of result.work_orders) {
                const prev = this._lastRejectCounts[wo.id] || 0;
                if (wo.reject_count > prev && prev > 0) {
                    const delta = wo.reject_count - prev;
                    this.showToast(
                        "Reject Detected!",
                        `${wo.name}: +${delta} reject(s) (total: ${wo.reject_count})`
                    );
                }
                this._lastRejectCounts[wo.id] = wo.reject_count;
            }
        }
    }

    showToast(title, message) {
        const id = ++this._toastIdCounter;
        this.state.toasts.push({ id, title, message });
        setTimeout(() => this.dismissToast(id), 5000);
    }

    dismissToast(id) {
        const idx = this.state.toasts.findIndex(t => t.id === id);
        if (idx >= 0) {
            this.state.toasts.splice(idx, 1);
        }
    }
}

registry.category("systray").add("ScrapToast", { Component: ScrapToast }, { sequence: 1000 });
