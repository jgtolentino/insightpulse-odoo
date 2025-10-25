import {Dialog} from "@web/core/dialog/dialog";
import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";
import {useRef} from "@odoo/owl";
import {user} from "@web/core/user";

const {Component} = owl;

function buildReportUrl(action, type, userContext) {
    let url = `/report/${type}/${action.report_name}`;
    const actionContext = action.context || {};
    if (action.data && Object.keys(action.data).length) {
        // Build a query string with `action.data` (it's the place where reports
        // using a wizard to customize the output traditionally put their options)
        url += `?options=${encodeURIComponent(JSON.stringify(action.data))}`;
        url += `&context=${encodeURIComponent(JSON.stringify(actionContext))}`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}`;
        }
        if (type === "html") {
            url += `?context=${encodeURIComponent(JSON.stringify(userContext))}`;
        }
    }
    return url;
}

async function download_function(action, options, env) {
    const type = action.report_type === "qweb-pdf" ? "pdf" : action.report_type;
    const userContext = {
        ...user.context,
        encrypt_password: action.context?.encrypt_password,
    };
    const url = buildReportUrl(action, type, userContext);
    env.services.ui.block();
    try {
        await download({
            url: "/report/download",
            data: {
                data: JSON.stringify([url, action.report_type]),
                context: JSON.stringify(userContext),
            },
        });
    } finally {
        env.services.ui.unblock();
    }
    if (action.close_on_report_download) {
        return env.services.action.doAction(
            {type: "ir.actions.act_window_close"},
            {onClose: options.onClose}
        );
    }
    options.onClose?.();
    return true;
}

class EncryptDialog extends Component {
    setup() {
        this.passwordRef = useRef("password");
    }
    onClick() {
        const password = this.passwordRef.el?.value || false;
        const action = {
            ...this.props.action,
            context: {
                ...this.props.action.context,
                encrypt_password: password,
            },
        };
        return download_function(action, this.props.options, this.props.env);
    }
}

EncryptDialog.components = {Dialog};
EncryptDialog.template = "report_qweb_encrypt.EncryptDialogBody";

registry
    .category("ir.actions.report handlers")
    .add("qweb-pdf-password", async (action, options, env) => {
        if (action.encrypt === "manual" && action.report_type === "qweb-pdf") {
            return env.services.dialog.add(EncryptDialog, {action, options, env});
        }
        return false;
    });
