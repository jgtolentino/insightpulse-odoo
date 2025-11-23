/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Finance PPM Dashboard JavaScript
 *
 * Provides client-side functionality for ECharts-based PPM dashboard
 */

const financePPMDashboard = {
    dependencies: [],

    start() {
        console.log("Finance PPM Dashboard loaded");
    },
};

registry.category("main_components").add("financePPMDashboard", financePPMDashboard);
