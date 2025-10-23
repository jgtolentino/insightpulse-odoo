/** @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class BiChartViewer extends Component {
    static template = "bi_superset_agent.ChartViewer";
    static props = {
        chartUrl: String,
        height: { type: Number, optional: true },
    };

    setup() {
        this.height = this.props.height || 640;
    }

    get chartUrl() {
        return this.props.chartUrl;
    }

    get iframeStyle() {
        return `width: 100%; height: ${this.height}px; border: none;`;
    }
}

registry.category("fields").add("bi_chart_viewer", {
    component: BiChartViewer,
});
